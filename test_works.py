import unittest
from dagster import materialize
from bdrc_works import works


class MyTestCase(unittest.TestCase):

    def test_works_materialization(self):
        result = materialize([works])
        self.assertTrue(result.success)  # add assertion here


if __name__ == '__main__':
    unittest.main()
