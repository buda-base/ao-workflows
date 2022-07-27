"""
Routines to do the iiifpres crawl
"""

from dagster import op
import boto3
import json

from v_m_b.ImageRepository.ImageRepositoryFactory import ImageRepositoryFactory
from v_m_b.VolumeInfo.VolumeInfoBuda import VolumeInfoBUDA

BUDA_BUCKET = "archive.tbrc.org"
BUDA_PREFIX = "Works/"

# See v-m-b manifestcommons
VMT_BUDABOM: str = 'fileList.json'
VMT_BUDABOM_JSON_KEY: str = 'filename'
VMT_DIM: str = 'dimensions.json'


def get_dimensions(work_name: str) -> object:
    """
    Fetches the dimenstop
    :param bom_path:  full s3 path to BOM
    :return:
    """
    # Borrowed from v-m-b manifestCommons.py:prolog
    session = boto3.session.Session(region_name='us-east-1')
    client = session.client('s3')
    dest_bucket = session.resource('s3').Bucket(BUDA_BUCKET)
    image_repository = ImageRepositoryFactory().repository('s3', VMT_BUDABOM,
                                                           client=client, bucket=dest_bucket)
    vol_infos: [] = VolumeInfoBUDA(image_repository).fetch(work_name)
    return vol_infos


if __name__ == '__main__':
    get_dimensions('W00EGS1015752')
