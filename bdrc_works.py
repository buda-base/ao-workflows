from dagster import asset

@asset(
    metadata={"owner":"jmk@tbrc.org","domain": "ao"}
)
def works():
    work_list:[] = []
    with open('data/scans.lst', 'r') as df:
        work_list = [x.strip() for x in df.readlines()]

    return work_list