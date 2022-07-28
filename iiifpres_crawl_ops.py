"""Operations for the iiifpres crawl"""

from dagster import op, materialize, get_dagster_logger
from bdrc_works import  works

@op
def get_works() ->[]:
    """
    One operation to get all the works. Just uses the asset
    :return: works asset
    """
    return works()

@op
def get_image_groups(work: str) -> []:
    """
    Return the s3 paths to the image groups in the work
    :param work:
    :return:
    """

@op
def test_work_json(work:str) -> bool:
    """
    Test all the work's jsons
    :param work:
    :return:
    """
    failed_dims: [] = [ { "image_group" : x, "valid":  test_ig_dim(x)} for x in get_image_groups(work) ]

@op
def test_ig_dim(dim_s3_path: str) -> bool:



@job
def iiifpres_crawl():
    get_works().map(test_work_json)