import unittest

from iiifpres_crawl_ops import iiifpres_crawl


from crawl_utils import crawl_utils
from iiifpres_crawl_ops import validate_dims


class MyTestCase(unittest.TestCase):

    # def test_works_materialization(self):
    #     from dagster import materialize
    #     from bdrc_works import works
    #     result = materialize([works])
    #     self.assertTrue(result.success)  # add assertion here

    def setUp(self):
        self.utils = crawl_utils()

    def test_igs(self):
        """
        Test image group acquisition
        :return:
        """

        bloop = self.utils.get_dimensions_s3_keys('W10736')

        # Work has 24 volumes
        self.assertEqual(24, len(bloop))

        # Work key should contain the S3 hex pair
        self.assertTrue(all(['/32/' in x for x in bloop]))


    @unittest.skip("Thirsty, resource dependent")
    def test_get_obj(self):
        Frelm = self.utils.get_dimension_values('Works/32/W10736/images/W10736-1240/dimensions.json')

    def test_filename_sort_validate_fails(self):
        """
        Ensure an invalid json fails
        :return:
        """
        bad_value: [] = [
            {
                "filename" : "W0001.jpeg",
                "height" : "500",
                "width" : "500",
            },
            {
                "filename" : "W0002.jpeg",
                "height" : "500",
                "width" : "500",
            },
            {
                "filename" : "W0004.jpeg",
                "height" : "500",
                "width" : "500",
            },
            {
                "filename" : "W0003.jpeg",
                "height" : "500",
                "width" : "500",
            }
        ]

        # Act
        val, reason = validate_dims(bad_value)
        self.assertFalse(val,"Should be false")
        self.assertEqual("sorted:False has_dims:True", reason)

    def test_negative_height_validate_fails(self):
        """
        Ensure an invalid json fails
        :return:
        """
        bad_value: [] = [
            {
                "filename" : "W0001.jpeg",
                "height" : "500",
                "width" : "500",
            },
            {
                "filename" : "W0004.jpeg",
                "height" : "-500",
                "width" : "500",
            }
        ]

        # Act
        val, reason = validate_dims(bad_value)
        self.assertFalse(val,"Should be false")
        self.assertEqual("sorted:True has_dims:False", reason)

    def test_negative_width_validate_fails(self):
        """
        Ensure an invalid json fails
        :return:
        """
        bad_value: [] = [
            {
                "filename" : "W0001.jpeg",
                "height" : "500",
                "width" : "-500",
            },
            {
                "filename" : "W0004.jpeg",
                "height" : "500",
                "width" : "500",
            }
        ]

        # Act
        val, reason = validate_dims(bad_value)
        self.assertFalse(val,"Should be false")
        self.assertEqual("sorted:True has_dims:False", reason)

    def test_missing_height_validate_fails(self):
        """
        Ensure an invalid json fails
        :return:
        """
        bad_value: [] = [
            {
                "filename": "W0001.jpeg",
                "NOPEheight": "500",
                "width": "500",
            },
            {
                "filename": "W0002.jpeg",
                "height": "500",
                "width": "500",
            },
            {
                "filename": "W0003.jpeg",
                "height": "500",
                "width": "500",
            },
            {
                "filename": "W0004.jpeg",
                "height": "-500",
                "width": "500",
            }
        ]

        # Act
        val, reason = validate_dims(bad_value)
        self.assertFalse(val, "Should be false")
        self.assertEqual("sorted:True has_dims:False", reason)

    def test_missing_width_validate_fails(self):
        """
        Ensure an invalid json fails
        :return:
        """
        bad_value: [] = [
            {
                "filename": "W0001.jpeg",
                "height": "500",
                "width": "500",
            },
            {
                "filename": "W0002.jpeg",
                "height": "500",
                "NOPEwidth": "500",
            }
        ]

        # Act
        val, reason = validate_dims(bad_value)
        self.assertFalse(val, "Should be false")
        self.assertEqual("sorted:True has_dims:False", reason)

    @unittest.skip("Dont launch a dag")
    def test_ops(self):
        """
        See about testing dagster concepts
        :return:
        """
        result = iiifpres_crawl.execute_in_process()
        self.assertEqual(True, result.success)



if __name__ == '__main__':
    unittest.main()
