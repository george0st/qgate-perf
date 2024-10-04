import unittest
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.output_setup import OutputSetup
import time
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

def prf_calibration_ten_ms(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchonization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while (True):

        # START - performance measure for specific part of code
        probe.start()

        for r in range(run_setup.bulk_row * run_setup.bulk_col):
            time.sleep(0.01)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    return probe


class TestCaseCoreEvaluation(unittest.TestCase):
    """
    Test, if calculation of performance is correct

        IMPORTANT (main ideas)
          - all cases will have similar calls per second
          - the different duration time of tests does not change performance (calls per second)
          - peformance will affect size of bundle and amount of executors
    """
    OUTPUT_ADR = "../output/test_perf/"

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCaseCoreEvaluation.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_expected_output100ms_1(self):

        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                         executor_list = [[1,1]],
                                                         run_setup = setup,
                                                         return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 9 and perf[0].calls_sec <= 11)

    def test_expected_output100ms_2(self):
        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file = None)
        # first
        setup=RunSetup(duration_second=1, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 19 and perf[0].calls_sec <= 21)

        # second
        setup=RunSetup(duration_second=2, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 19 and perf[0].calls_sec <= 21)

        # third
        setup=RunSetup(duration_second=10, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 19 and perf[0].calls_sec <= 21)

    def test_expected_output100ms_3(self):
        generator = ParallelExecutor(prf_calibration_onehundred_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second=1, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 39 and perf[0].calls_sec <= 41)

        # second
        setup=RunSetup(duration_second=2, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 39 and perf[0].calls_sec <= 41)

        # third
        setup=RunSetup(duration_second=10, start_delay=0)
        state, perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 39 and perf[0].calls_sec <= 41)

    def test_expected_output10ms_1(self):

        generator = ParallelExecutor(prf_calibration_ten_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                         executor_list = [[1,1]],
                                                         run_setup = setup,
                                                         return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 90 and perf[0].calls_sec <= 110)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 90 and perf[0].calls_sec <= 110)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 90 and perf[0].calls_sec <= 110)

    def test_expected_output10ms_2(self):

        generator = ParallelExecutor(prf_calibration_ten_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                         executor_list = [[2,1]],
                                                         run_setup = setup,
                                                         return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 180 and perf[0].calls_sec <= 220)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 180 and perf[0].calls_sec <= 220)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 180 and perf[0].calls_sec <= 220)

    def test_expected_output10ms_3(self):

        OutputSetup().human_precision = 7
        generator = ParallelExecutor(prf_calibration_ten_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                         executor_list = [[4,1]],
                                                         run_setup = setup,
                                                         return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 360 and perf[0].calls_sec <= 440)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 360 and perf[0].calls_sec <= 440)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 5)
        state, perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  return_performance = True)
        self.assertTrue(state)
        self.assertTrue(perf[0].calls_sec >= 360 and perf[0].calls_sec <= 440)
