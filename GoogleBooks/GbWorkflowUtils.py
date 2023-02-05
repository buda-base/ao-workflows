"""
Helper utilities for workflow
"""
import requests
from requests import Response

# Can import as csv_f, json, or simple csv (one column)
BUDA_Get_GB_ReadyUrl: str = "https://purl.bdrc.io/query/table/AO_okforGB?&format=csv&pageSize=20000"
buda_work_prefix:str = "bdr:"

def get_gb_candidates() -> []:
    """
    Extract from BUDA
    :return:
    """

    # pattern from https://www.programcreek.com/python/example/68989/requests.HTTPError
    try:
        gb_ready: Response = requests.get(BUDA_Get_GB_ReadyUrl)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None
        else:
            raise

    return gb_ready.text.split('\n')

def transform_works(in_list:[str])-> int:
    """
    Transforms works into workIds
    :param in_list: "some lines"+"bdr:Wnnnn"+
    :type in_list:[str]
    :return: for every element containing bdr: return the work Id that goes with that work.
    Creates the work if needed
    """
    # 1. Remove everything that's not a work, and remove the prefix
    work_elems = [ x[len(buda_work_prefix):] for x in in_list if x.startswith(buda_work_prefix)]


# Just invoke for testing
if __name__ == '__main__':
    print(len(get_gb_candidates()))
