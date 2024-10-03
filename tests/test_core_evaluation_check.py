import os
import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.run_return import RunReturn
from qgate_perf.bundle_helper import BundleHelper
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.output_setup import OutputSetup
import time
from os import path
import shutil

def prf_calibration_onehundred_ms(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchonization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while (True):

        # START - performance measure for specific part of code
        probe.start()

        for r in range(run_setup.bulk_row * run_setup.bulk_col):
            time.sleep(0.1)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    return probe

class TestCaseCoreEvaluationCheck(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCaseCoreEvaluationCheck.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_expected_output1(self):
        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second = 1, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                         executor_list = [[1,1]],
                                                         run_setup = setup,
                                                         return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)

        setup=RunSetup(duration_second = 2, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)


        setup=RunSetup(duration_second = 10, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)

    def test_expected_output2(self):
        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[2,1]],
                                    run_setup=setup))

        setup=RunSetup(duration_second=2, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[2,1]],
                                    run_setup=setup))

        setup=RunSetup(duration_second=10, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[2,1]],
                                    run_setup=setup))

        # TODO: compare final performance

    def test_expected_output3(self):
        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[4,1]],
                                    run_setup=setup))

        setup=RunSetup(duration_second=2, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[4,1]],
                                    run_setup=setup))

        setup=RunSetup(duration_second=10, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=[[4,1]],
                                    run_setup=setup))

        # TODO: compare final performance
