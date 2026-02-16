from enum import Enum
import sys

from pendulum import datetime # for defining the policy enum
# Define an Enum for upload policies
class UploadIAPolicy(Enum):
    OK = "OKGo"
    SIZE_NO = "size"
    IMAGES_ONLY = "images_only"


"""
Translate this into python
#!/usr/bin/env bash
# 
#
# Reads a file that the get_works_for_activity -a IA prepares


# Example usage in should_upload_to_ia function:
# def should_upload_to_ia(policy: UploadIAPolicy, ...):
#     if policy == UploadIAPolicy.ALWAYS:
#         return True
#     elif policy == UploadIAPolicy.NEVER:
#         return False
#     elif policy == UploadIAPolicy.CONDITIONAL:
#         # custom logic
#         pass
# This script expects that the file is a csv that contains
#.... 0 - 1 headers
#.... 1+ lines containing two csv fields:  WorkName, Workpath

# shellcheck disable=SC2034
ME=$(basename "$(readlink -f $0)")
set -e
. ~/bin/init_sys.sh

# dip variables
# this is IA status check
# if you want this script to check whether or not something is in IA and not upload if it is, set it to 1
# if you want it to send everything to IA and update what is there, leave it empty
#
NO_UPLOAD_IF_EXISTS=
# dest_path="ia://"

#csv input file
in_file=${1:-/dev/stdin}
# jimk lib-issues-472: using just the work name, and will use
# the standalone depositIa.sh, which maintains its own archive path.
# This means that GetReadyFor IA is going to have to use a different output, not the
# single archive

# Std header from get_works_for_activity
header=(WorkName path)
# csv reading loop

while IFS=, read -ra arc_line; do

    # If the stop file exists (see ../dip-pump/MainPump.sh) then stop processing
    # set by MainPump.sh to indicate user termination
    if [[ -f $STOP_FLAG_FILE ]] ; then
	log_echo Stop file found $(ls -l $STOP_FLAG_FILE) breaking loop
	break
    fi

    # Debug
    #proof_of_life
    # continue

    #skip header
    if [[ ${arc_line[0]} == "${header[0]}" && ${arc_line[1]} == "${header[1]}" ]]; then
      continue
    fi

    #reading csv
    rid=${arc_line[0]}

    # jimk: Now that we're not using single archive as source for IA,
    # just use the archive source path. IA builds in a temp folder
    srcPath=${arc_line[1]}  
    #check to see if item is allowed to circulate in IA
    # dont even bother to build the IA zip if it can't go in IA.
    # Make a log, mark it done, move on.
    # W19992 tests this

  can_ia_query=$(printf "https://ldspdi.bdrc.io/query/ask/AO_should_upload_to_IA?R_RES=bdr:%s" ${rid})
–
   #this is a little noisy. -s and stderr redirect.
  # map any variant of "false" to empty, for future parsing if needed.
  goes_to_ia=$(curl -s "${can_ia_query}" 2> /dev/null | sed -e 's/^.*false.*$//I')

  # goes_to_ia is now not false, or empty [[ -z ... ]] would be true
  # This means we can upload
  if [[ -n $goes_to_ia  ]]; then

    # This tells us if we have to force the upload
    # no to not uploading means force uploading
    if [[ -z $NO_UPLOAD_IF_EXISTS ]]; then
      deposit_ia_flag=-f
    fi
    depositIa.sh "${deposit_ia_flag}" "$srcPath"
    # proof_of_life here to test signal handling

  else
    # jimk lib-issues 472 - we're taking IA out of the pipeline. There are no downstream
      # dependencies, so a work that cannot be uploaded will have a placeholder IA record.
      # register occurrence, but with a failure code
      # Uhh, that had the problem of not having these records pass
      # through single_archive_removed step, which requires an
      # upload to IA. So make the failure code a success code, and add a note.
      
    log_dip_id=$(log_dip -b "$(log_dip_date)" -e "$(log_dip_date)" -r "0" -a "IA" -w "${rid}" -c "Policy not allowed.")
    log_echo "Policy disallows update record id: ${log_dip_id}"
  fi
done <"${in_file}"

"""
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
    
