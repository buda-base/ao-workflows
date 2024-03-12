import pytest
"""
Test the GlacierStagingToSync DAG.
Structure inspired by:
https://stackoverflow.com/questions/50016862/grouping-tests-in-pytest-classes-vs-plain-functions
"""

from StagingGlacierProcess.glacier_staging_to_sync import *

# def test_ping():
#     gs_dag.test()
class TestGlacierStagingToSync:
    def test_ping(self):
        gs_dag.test()

