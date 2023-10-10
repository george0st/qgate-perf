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

def prf_test(run_return: RunReturn, run_setup: RunSetup):
    """ Function for performance testing"""

    # init (contain executor synchonization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col} [{run_return.probe}]")

    while (True):

        # START - performance measure for specific part of code
        probe.start()

        for r in range(run_setup.bulk_row * run_setup.bulk_col):
            time.sleep(0.001)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    run_return.probe=probe


class TestCaseGraph(unittest.TestCase):
    OUTPUT_ADR = "../output/test_graph/"

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCaseGraph.OUTPUT_ADR,True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_graph(self):
        generator = ParallelExecutor(prf_test,
                                     label="test",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=None)
        self.assertTrue(generator.run_bulk_executor([[10,10], [100,10]],
                                                    [[1,2,'Austria perf'], [2,2,'Austria perf'], [4,2,'Austria perf'],
                                                    [1,4,'Germany perf'],[2,4,'Germany perf'],[4,4,'Germany perf']],
                                                    setup))
        generator.create_graph(self.OUTPUT_ADR)

    def test_graph2(self):
        generator = ParallelExecutor(prf_test,
                                     label="test",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run(1,1, setup))
        generator.create_graph(self.OUTPUT_ADR)

    def test_graph3(self):
        generator = ParallelExecutor(prf_test,
                                     label="test",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run_executor([[2,2]], setup))
        generator.create_graph(self.OUTPUT_ADR)
