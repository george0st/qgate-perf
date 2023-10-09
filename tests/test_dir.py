import os
import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.run_return import RunReturn
import time
from os import path
import shutil

class TestCaseDir(unittest.TestCase):
    OUTPUT_ADR = "../output/test_dir/"

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCaseDir.OUTPUT_ADR,True)
    @classmethod
    def tearDownClass(cls):
        pass

    def test_dir(self):
        generator = ParallelExecutor(None,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file= path.join(self.OUTPUT_ADR,"test_gil_impact_test.txt"))

        self.assertTrue(generator.one_run())

