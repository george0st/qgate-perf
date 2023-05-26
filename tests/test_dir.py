import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.run_return import RunReturn
import time

class TestCaseDir(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dir(self):
        generator = ParallelExecutor(None,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="../output/aaa/test_gil_impact_test.txt")

        generator.one_run()
