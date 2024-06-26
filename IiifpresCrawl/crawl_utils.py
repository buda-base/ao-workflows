"""
Routines that support the iiifpres crawl
"""
import gzip
import hashlib
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from v_m_b import VolumeInfo, AOLogger

from v_m_b.ImageRepository.ImageRepositoryFactory import ImageRepositoryFactory
from v_m_b.VolumeInfo.VolInfo import VolInfo
from v_m_b.VolumeInfo.VolumeInfoBuda import VolumeInfoBUDA
from v_m_b.manifestBuilder import upload_volume

BUDA_BUCKET = "archive.tbrc.org"
BUDA_PREFIX = "Works/"

# See v-m-b manifestcommons
VMT_BUDABOM: str = 'fileList.json'
VMT_BUDABOM_JSON_KEY: str = 'filename'
VMT_DIM: str = 'dimensions.json'


class crawl_utils():
    s3_client = None
    s3: boto3.resource
    logger: AOLogger

    def __init__(self):
        """
        Initialize some invariants
        """
        self.s3_client = boto3.client('s3')
        self.s3 = boto3.resource('s3')

        # Borrowed from v-m-b manifestCommons.py:prolog
        self.image_repository = ImageRepositoryFactory().repository('s3', VMT_BUDABOM, client=self.s3_client,
                                                                    bucket=self.s3.Bucket(BUDA_BUCKET))
        self.logger = AOLogger.AOLogger('crawl_utils', 'info', Path("."))

    def get_dimensions_s3_keys(self, work_rid: str) -> []:
        """
        Fetches the paths to the dimension files, using BUDA to get the image groups
        :return:
        """

        vol_infos: [] = VolumeInfoBUDA(self.image_repository).fetch(work_rid)

        md5 = hashlib.md5(str.encode(work_rid))
        two = md5.hexdigest()[:2]

        return [f"{BUDA_PREFIX}{two}/{work_rid}/images/{work_rid}-{x.imageGroupID}/{VMT_DIM}" for x in vol_infos]

    def fix_one(self, work_rid: str, image_group: str):
        """
        Fix one instance
        :return:
        """

        # Should be only one, gag if none
        vol_info: VolInfo =  [x for x in VolumeInfoBUDA(self.image_repository).fetch(work_rid) if x.imageGroupID in image_group][0]

        upload_volume(work_rid, vol_info, self.image_repository, self.logger)

    def get_dimension_values(self, dim_s3_path: str) -> []:
        """
        Download, decompress, and deserialize a dimensions.json
        :param dim_s3_path:list of dictionaries
        :return: list of file infos
        """
        import io
        import json

        operand: str = f"s3://{BUDA_BUCKET}/{dim_s3_path}"
        try:
            dim_stream = io.BytesIO()
            self.s3_client.download_fileobj(BUDA_BUCKET, dim_s3_path, dim_stream)
            dim_stream.seek(0)
            dims: str = gzip.decompress(dim_stream.read()).decode()
            return json.loads(dims)
        except ClientError as ce:
            return [{"ERROR": f"S3ClientError {ce}", "object": operand}]
        except Exception as e:
            return [{"ERROR": f"Error {e}", "object": operand}]
