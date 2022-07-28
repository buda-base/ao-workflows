import unittest

from iiifpres_crawl_ops import iiifpres_crawl

from dagster import JobDefinition
from crawl_utils import crawl_utils
from iiifpres_crawl_ops import get_works, test_work_json


class MyTestCase(unittest.TestCase):

    # def test_works_materialization(self):
    #     from dagster import materialize
    #     from bdrc_works import works
    #     result = materialize([works])
    #     self.assertTrue(result.success)  # add assertion here

    def test_igs(self):
        fff = crawl_utils()
        bloop = fff.get_dimensions_s3_keys('W10736')
        self.assertEqual(24, len(bloop))

    def test_get_obj(self):
        fff = crawl_utils()
        Frelm = fff.get_dimension_values('Works/32/W10736/images/W10736-1240/dimensions.json')

    def test_ops(self):
        """
        See about testing dagster concepts
        :return:
        """
        result = iiifpres_crawl.execute_in_process()
        self.assertEqual(True, result.success)



if __name__ == '__main__':
    unittest.main()
