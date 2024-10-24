import unittest
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.output_setup import OutputSetup
from time import sleep
from qgate_perf.output_result import PerfResults
import shutil


def prf_calibration_100_ms(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchronization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while 1:

        # START - performance measure for specific part of code
        probe.start()

        sleep(0.1)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    return probe

def prf_calibration_10_ms(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchronization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while 1:

        # START - performance measure for specific part of code
        probe.start()

        sleep(0.01)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    return probe

def prf_calibration_4_ms(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchronization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while 1:

        # START - performance measure for specific part of code
        probe.start()

        sleep(0.004)

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
          - performance will affect size of bundle and amount of executors
    """
    OUTPUT_ADR = "../output/test_perf/"

    @classmethod
    def setUpClass(cls):
        OutputSetup().human_precision = 7
        shutil.rmtree(TestCaseCoreEvaluation.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        OutputSetup().human_precision = OutputSetup().HUMAN_PRECISION

    def check_result(self, result: PerfResults, perf_min, perf_max):
        # check the result
        self.assertTrue(result.state)
        self.assertTrue(result[0][1].call_per_sec >= perf_min and result[0][1].call_per_sec <= perf_max)

    def check_raw_result(self, result: PerfResults, perf_min, perf_max):
        # check the result for raw value
        self.assertTrue(result.state)
        self.assertTrue(result[0][1].call_per_sec_raw >= perf_min and result[0][1].call_per_sec_raw <= perf_max)

    def test_expected_output100ms_1(self):

        generator = ParallelExecutor(prf_calibration_100_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 9,10)


        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 9, 10)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 9, 10)

    def test_expected_output100ms_2(self):
        generator = ParallelExecutor(prf_calibration_100_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file = None)
        # first
        setup=RunSetup(duration_second=1, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)

        self.check_result(perf,19,20)

        # second
        setup=RunSetup(duration_second=2, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)
        self.check_result(perf,19,20)

        # third
        setup=RunSetup(duration_second=10, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[2,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)
        self.check_result(perf,19,20)

    def test_expected_output100ms_3(self):
        generator = ParallelExecutor(prf_calibration_100_ms,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second=1, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)
        self.check_result(perf, 39, 40)

        # second
        setup=RunSetup(duration_second=2, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)
        self.check_result(perf, 39, 40)

        # third
        setup=RunSetup(duration_second=10, start_delay=0)
        perf = generator.run_bulk_executor(bulk_list=[[1,1]],
                                                  executor_list=[[4,1]],
                                                  run_setup=setup,
                                                  performance_detail= True)
        self.check_result(perf, 39, 40)

    def test_expected_output010ms_1(self):

        generator = ParallelExecutor(prf_calibration_10_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 90, 100)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 90, 100)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 90, 100)

    def test_expected_output010ms_2(self):

        generator = ParallelExecutor(prf_calibration_10_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 180, 200)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 180, 200)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 180, 200)

    def test_expected_output010ms_3(self):

        generator = ParallelExecutor(prf_calibration_10_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 360, 400)

        # self.assertTrue(state)
        # self.assertTrue(perf[0].calls_sec >= 360 and perf[0].calls_sec <= 400)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 360, 400)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 5)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 360, 400)

    def test_expected_output004ms_1(self):

        generator = ParallelExecutor(prf_calibration_4_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 200, 250)


        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 200, 250)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[1,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 200, 250)

    def test_expected_output004ms_2(self):

        generator = ParallelExecutor(prf_calibration_4_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 400, 500)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 400, 500)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[2,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 400, 500)

    def test_expected_output004ms_3(self):

        generator = ParallelExecutor(prf_calibration_4_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup=RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 800, 1000)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 800, 1000)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[1,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 800, 1000)

    def test_expected_output004ms_bundle(self):

        generator = ParallelExecutor(prf_calibration_4_ms,
                                     label = "GIL_impact",
                                     detail_output = True,
                                     output_file = None)

        # first
        setup = RunSetup(duration_second = 1, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[2,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 1600, 2000)
        self.check_raw_result(perf, 800, 1000)

        # second
        setup=RunSetup(duration_second = 2, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[3,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail = True)
        self.check_result(perf, 2400, 3000)
        self.check_raw_result(perf, 800, 1000)

        # third
        setup=RunSetup(duration_second = 10, start_delay = 0)
        perf = generator.run_bulk_executor(bulk_list = [[4,1]],
                                                  executor_list = [[4,1]],
                                                  run_setup = setup,
                                                  performance_detail= True)
        self.check_result(perf, 3200, 4000)
        self.check_raw_result(perf, 800, 1000)
