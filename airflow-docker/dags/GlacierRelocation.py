"""
For Archive ops 1158 https://github.com/buda-base/archive-ops/issues/1158
Write a dag to scan the glacier.archive.bdrc.org bucket for mislocated works. These are
works whose archival copies were relocated from Archive0 and 1 to Archive 1,2,3.
By definition, they are:
Archive0, 25 - 49 --> Archive1
Archive1, 50-74 --> Archive2
Archive1, 75-99 --> Archive3

The DAG will:
- restore all the existing works
- listen for a restore complete notification (see `glacier_staging_to_sync)
- copy the restored object to the correct location, but extend the key with a suffix,
'moved_from_archivex' or 'moved_from_archivex'
 - delete the original object
"""

import s3pathlib
from pprint import pp

from s3pathlib import S3Path

map_remap: {} = {
    "Archive0": [{"values": [25, 49], "dest": "Archive1"}],
    "Archive1": [{"values": [50, 74], "dest": "Archive2"}, {"values": [75, 99], "dest": "Archive3"}]
}


# Write a routine to return map_remap "dest" for a given path ending with two digits. If the digits are between the "values" range, return the "dest"
def get_remap_dest(bin_work_parts:[str]) -> str:
    # Get the last two digits
    try:
        bin_name = bin_work_parts[0]
        digits = int(bin_work_parts[1])
        # Get the map_remap for the bin_name
        remap = map_remap.get(bin_name)
        if remap:
            for r in remap:
                if r["values"][0] <= digits <= r["values"][1]:
                    return r["dest"]
    except IndexError:
        pp(f" Cant parse {bin_work_parts}")
    return None


# Walk the glacier.archive.bdrc.org bucket, looking for works that have been mislocated
def scan_glacier_bucket():
    sum_nw:int = 0
    glacier_bucket = s3pathlib.S3Path("s3://glacier.archive.bdrc.org")
    for bin_key in glacier_bucket.iterdir():
        for bin_section in bin_key.iterdir():
            dest_bin = get_remap_dest(bin_section.parts)
            if not dest_bin:
                # print(f"      Skipping {bin_section}")
                continue
            #
            section_works:[s3pathlib.S3Path] = [ x for x in bin_section.iterdir() if x.is_dir() ]

            # count the children of a moved section
            n_works: int = len(section_works)
            sum_nw += n_works
            print(f"Moving {n_works} works from  {bin_section} to { dest_bin}")
            for work in section_works:
                work_name = f"Older_archive_{work.basename}_arn_here"
                source_string: str = f"{bin_section.arn}{work.basename}"
                # Write the original destination into Wnnnn.zip, and move it to the new location
                new_dest: S3Path = glacier_bucket / dest_bin / bin_section.basename / work.basename / work_name
                with new_dest.open( "w") as f:
                    f.write(f"{source_string}\n")

                print(f"copied {work}  from  {bin_section} to {new_dest}")
    print("total moved", sum_nw, sep=":")


if __name__ == '__main__':
    scan_glacier_bucket()
