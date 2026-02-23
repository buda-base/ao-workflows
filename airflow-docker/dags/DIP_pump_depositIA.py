from enum import Enum
import sys
import os
import csv
import tempfile
import shutil
from pathlib import Path
import requests
import zipfile
import logging
from pendulum import datetime
from internetarchive import upload, search_items

# Airflow logger
af_log = logging.getLogger("airflow.task")

class UploadIAPolicy(Enum):
  OK = "OKGo"
  SIZE_NO = "size"
  IMAGES_ONLY = "images_only"
  POLICY = "policy"
  POLICY_UNKNOWN = "policy_unknown" # for failures in the policy check, 
  
MAX_DISK_GB = 800
ZIP_EXCLUDE_IMG_JSON = ["./images/*/*.json", "./images/*/*.JSON"]

def get_directory_size(path_to_work: Path) -> int:
  return sum(f.stat().st_size for f in path_to_work.rglob('*') if f.is_file())

def get_upload_policy(rid: str, rid_path: Path) -> UploadIAPolicy:
  can_ia_query = f"https://ldspdi.bdrc.io/query/ask/AO_should_upload_to_IA?R_RES=bdr:{rid}"
  try:
    resp = requests.get(can_ia_query, timeout=10)
    goes_to_ia = resp.text.strip().lower() != "false"
  except Exception as e:
    af_log.error(f"Policy check failed for {rid}: {e}")
    return UploadIAPolicy.POLICY_UNKNOWN
  if not goes_to_ia:
    return UploadIAPolicy.POLICY
  size_gb = get_directory_size(rid_path) / (1024 ** 3)
  if size_gb > MAX_DISK_GB:
    images_gb = get_directory_size(rid_path / 'images') / (1024 ** 3)
    if images_gb > MAX_DISK_GB:
      return UploadIAPolicy.SIZE_NO
    else:
      return UploadIAPolicy.IMAGES_ONLY
  return UploadIAPolicy.OK

def zip_work( src_path: Path, zip_path: Path, images_only: bool = False, exclude_img_json=None):
  """
  Zips the work at src_path into zip_path.
  If images_only is True, only zips the images/ subfolder (excluding JSONs).
  Otherwise, zips images/ first, then all other subfolders except meta/.
  """
  exclude_img_json = exclude_img_json or []
  with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add images/ first
    images_dir = src_path / 'images'
    if images_dir.exists():
      for root, dirs, files in os.walk(images_dir):
        for file in files:
          file_path = Path(root) / file
          rel_path = file_path.relative_to(src_path)
          # Exclude JSON files in images
          if any(file_path.match(pattern) for pattern in exclude_img_json):
            continue
          zf.write(file_path, rel_path)
    if not images_only:
      # Add all other subfolders except meta/ and images/
      for item in src_path.iterdir():
        if item.name in ('images', 'meta'):
          continue
        if item.is_dir():
          for root, dirs, files in os.walk(item):
            for file in files:
              file_path = Path(root) / file
              rel_path = file_path.relative_to(src_path)
              zf.write(file_path, rel_path)
        elif item.is_file():
          rel_path = item.relative_to(src_path)
          zf.write(item, rel_path)

def populate_meta(rid: str, meta_dir: Path):
  """
  Populates the meta directory for the work using a remote metadata service (curl equivalent).
  """
  meta_dir.mkdir(parents=True, exist_ok=True)
  # TODO: Example: download metadata file (replace with actual endpoint and logic)
  meta_url = f"https://ldspdi.bdrc.io/works/meta/{rid}"
  meta_file = meta_dir / f"{rid}_meta.json"
  try:
    resp = requests.get(meta_url, timeout=10)
    resp.raise_for_status()
    with open(meta_file, 'wb') as f:
      f.write(resp.content)
    af_log.info(f"Downloaded metadata for {rid} to {meta_file}")
  except Exception as e:
    af_log.error(f"Failed to download metadata for {rid}: {e}")

# TODO: return status code for DipLog  
def upload_to_ia(rid: str, zip_path: Path):
  ia_id = f"bdrc-{rid}"
  af_log.info(f"Uploading {zip_path} to Internet Archive as {ia_id}")
  r = upload(ia_id, [str(zip_path)], metadata={"mediatype": "texts"}, retries=3, verbose=True, delete=True, checksum=True, quiet=True)
  for result in r:
    if result.status_code == 200:
      af_log.info(f"Upload successful for {ia_id}")
    else:
      af_log.error(f"Upload failed for {ia_id}: {result.status_code} {result.message}")

def process_work(rid: str, src_path: Path):
  """
  Processes a single work: 
  checks IA upload policy, 
  prepares zip, and uploads if allowed.
  args:   
    rid: the record ID of the work
    src_path: the path to the work's files on disk
    returns: None, but logs outcomes and uploads to IA if policy allows
  """
  policy = get_upload_policy(rid, src_path)
  if policy == UploadIAPolicy.POLICY:
    # TODO: DipLog this outcome with a success code, to prevent retry, and a dip_comment citing policy failure.
    af_log.info(f"Work {rid} does not meet IA upload policy. Skipping upload.")
    return
  if policy == UploadIAPolicy.SIZE_NO:
    af_log.info(f"Work {rid} is over {MAX_DISK_GB} GB, cannot be uploaded to IA.")
    # TODO: DipLog this outcome with a success code, to prevent retry, dip_comment citing size limit
    return
  images_only = (policy == UploadIAPolicy.IMAGES_ONLY)
  with tempfile.TemporaryDirectory() as tmpdir:
    arch_home = Path(tmpdir)
    meta_dir = arch_home / 'meta'
    populate_meta(rid, meta_dir)
    zip_path = arch_home / f"bdrc-{rid}_bdrc.zip"
    zip_work(src_path, zip_path, images_only=images_only, exclude_img_json=ZIP_EXCLUDE_IMG_JSON)
    upload_to_ia(rid, zip_path)

def main(csv_file: str):
  with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
      rid = row['WorkName']
      src_path = Path(row['path'])
      if not src_path.exists():
        af_log.error(f"Source path {src_path} not found for {rid}")
        continue
      process_work(rid, src_path)

if __name__ == "XX__main__":
  if len(sys.argv) < 2:
    print("Usage: python DIP_pump_depositIA.py <input_csv>")
    sys.exit(1)
  main(sys.argv[1])
    #check to see if item is allowed to circulate in IA
    # dont even bother to build the IA zip if it can't go in IA.
    # Make a log, mark it done, move on.
    # W19992 tests this

  # can_ia_query=$(printf "https://ldspdi.bdrc.io/query/ask/AO_should_upload_to_IA?R_RES=bdr:%s" ${rid})

   #this is a little noisy. -s and stderr redirect.
  # map any variant of "false" to empty, for future parsing if needed.
  # goes_to_ia=$(curl -s "${can_ia_query}" 2> /dev/null | sed -e 's/^.*false.*$//I')

  # goes_to_ia is now not false, or empty [[ -z ... ]] would be true
  # This means we can upload
#   if [[ -n $goes_to_ia  ]]; then

#     # This tells us if we have to force the upload
#     # no to not uploading means force uploading
#     if [[ -z $NO_UPLOAD_IF_EXISTS ]]; then
#       deposit_ia_flag=-f
#     fi
#     depositIa.sh "${deposit_ia_flag}" "$srcPath"
#     # proof_of_life here to test signal handling

#   else
#     # jimk lib-issues 472 - we're taking IA out of the pipeline. There are no downstream
#       # dependencies, so a work that cannot be uploaded will have a placeholder IA record.
#       # register occurrence, but with a failure code
#       # Uhh, that had the problem of not having these records pass
#       # through single_archive_removed step, which requires an
#       # upload to IA. So make the failure code a success code, and add a note.
      
#     log_dip_id=$(log_dip -b "$(log_dip_date)" -e "$(log_dip_date)" -r "0" -a "IA" -w "${rid}" -c "Policy not allowed.")
#     log_echo "Policy disallows update record id: ${log_dip_id}"
#   fi
# done <"${in_file}"

# determine if a rid should be upploaded to IA
from asyncio import subprocess
from pathlib import Path
from archive_ops import DipLog  
import logging

# airflow.task is a well-known af logger
af_log = logging.getLogger("airflow.task")

#Create Enumerable for policy check result 




def get_directory_size(path_to_work: Path) -> int:
    return sum(f.stat().st_size for f in path_to_work.rglob('*') if f.is_file())

# TODO: Compare with Copilot get_upload_policy 
def get_upload_policy(rid: str, rid_path: Path) -> UploadIAPolicy:
    """
    Returns the UploadIAPolicy corresponding the to the work:
     UploadIAPolicy.OK if the work with the given rid:
      - meets the library policy
      - is under 800 GB.
     UploadIAPolicy.POLICY if the work with the given rid does not meet 
     the library policy - it is not tested for size
     UploadIAPolicy.SIZE_NO if the work with the given rid meets the
        policy, but min(size of the work, size of the images) is over 800 GB.
     UploadIAPolicy.IMAGES_ONLY if the work is over 800GB, but the images are smaller.
    """
    can_ia_query = f"https://ldspdi.bdrc.io/query/ask/AO_should_upload_to_IA?R_RES=bdr:{rid}"
    goes_to_ia = subprocess.run(["curl", "-s", can_ia_query], capture_output=True, text=True).stdout.strip()
    policy: bool = goes_to_ia.lower() != "false"
    if not policy:
        return UploadIAPolicy.POLICY
    # Test the rid_path size, if over 800 GB, return SIZE_NO
    size_gb = get_directory_size(rid_path) / (1024 ** 3)
    if size_gb > 800:
        images_gb = get_directory_size(rid_path / 'images') / (1024 ** 3)
        if images_gb > 800:
            return UploadIAPolicy.SIZE_NO
        else:
            return UploadIAPolicy.IMAGES_ONLY
    return UploadIAPolicy.OK


if __name__ == "__main__":
    # Example usage
    rid = "W12345"
    rid_path = Path("/path/to/work")
    rid_upload_policy: UploadIAPolicy = get_upload_policy(rid, rid_path)
    #
    # TODO: Update for when in docker
    dl: DipLog = DipLog('qa:~/.config/bdrc/db_apps.config')
    if rid_upload_policy != UploadIAPolicy.OK:
        # Write a succesful log_dip entry here - this prevents retry.
        # The polcity failures are largely immuatable. If the work has to change,
        # that means it should be rearchived, even with a trivial change.
        # Even in an incremental archive,the whole archive is uploaded to IA
        if rid_upload_policy == UploadIAPolicy.POLICY:
            dip_message = f"Work {rid} does not meet IA upload policy."
        elif rid_upload_policy == UploadIAPolicy.SIZE_NO: 
            # Calculate image sizes. If they are over 800 GB, we wont upload,
            # otherwise we'll upload images/ only.
            images_size = get_directory_size(rid_path / 'images') 
            if images_size / (1024 ** 3) > 800:
                dip_message = f"Work {rid} is over 800 GB, and cannot be uploaded to IA."
            else:
                rid_upload_policy = UploadIAPolicy.OK
        if rid_upload_policy != UploadIAPolicy.OK:
          af_log.info(dip_message)
          # Use DipLog to log the policy failure, but with a success code, to prevent retry.
          nownow = datetime.now()
          log_dip_id = dl.set_dip(
              activity_name='IA',
                  begin_t=nownow,
                  end_t=nownow,
                  s_path=str(rid_path),
                  work_name=rid,
                  ac_result=0,
                  comment=dip_message)
          af_log.info(f"{dip_message} dip_id {log_dip_id}")
          sys.exit(0)
      # and just return, without uploading to IA
      #
    # Create a temporary directory
    # Create the structure, metadata.
    # Populate the metadata, as in archive_ops/scripts/ia/createe_metadata.sh
    # Add meta to a zip file
    # Add images to the zip file, excluding js or json (see script)
    # Start the dip_log timer here
    if rid_upload_policy == UploadIAPolicy.IMAGES_ONLY:
        # Just build the zip with what we have
        pass
    else:
        pass
        # Add all the archival material to the zip
    # Upload the zip to IA, using he ia library 
    
