import os
import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor, InitCallSetting
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.run_return import RunReturn
from qgate_perf.bundle_helper import BundleHelper
from qgate_perf.executor_helper import ExecutorHelper
import time
from os import path
import shutil

def prf_GIL_impact(run_return: RunReturn, run_setup: RunSetup):
    """ Function for performance testing"""

    try:

        # init (contain executor synchonization, if needed)
        probe = ParallelProbe(run_setup)

        if run_setup.is_init:
            print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col} [{run_return.probe}]")

        while (True):

            # START - performance measure for specific part of code
            probe.start()

            for r in range(run_setup.bulk_row * run_setup.bulk_col):
                time.sleep(0)

            # STOP - performance measure specific part of code
            if probe.stop():
                break

        if run_setup.param("generate_error"):
            raise Exception('Simulated error')

        # return outputs
        run_return.probe=probe

    except Exception as ex:
        # return outputs in case of error
        run_return.probe=ParallelProbe(None, ex)

class TestCasePerf(unittest.TestCase):

    OUTPUT_PERF_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCasePerf.OUTPUT_PERF_ADR,True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_one_run(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        self.assertTrue(generator.one_run())

    def test_one_run_param(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting={"aa":10,
               "name": "Adam"}

        self.assertTrue(generator.one_run(RunSetup(parameters=setting)))

    def test_init_run(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting={"aa":10,
               "name": "Adam"}

        self.assertTrue(generator.init_run(RunSetup(parameters=setting)))
        self.assertTrue(generator.init_run())

    def test_testrun_exception(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting={"generate_error": "yes"}

        # expected False (exception) because "generate_error"
        self.assertFalse(generator.test_run(RunSetup(parameters=setting),print_output=True))

    def test_testrun(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        self.assertTrue(generator.test_run(print_output=True))

    def test_testrun_setup(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting = {"aa": 10,
                   "name": "Adam"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertTrue(generator.test_run(run_setup=setup, print_output=True))

    def test_run(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=4, start_delay=2)
        self.assertTrue(generator.run(2, 2, setup))

    def test_run_exeption(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run(2, 2, setup))


    def test_run_executor(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=4, start_delay=2)
        self.assertTrue(generator.run_executor([[1,1], [2,2]], setup))

    def test_run_executor_exception(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertFalse(generator.run_executor([[1,1]], setup))

    def test_run_bulk_executor(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2], [1,10]],
                                    executor_list=[[1,1], [2,2]],
                                    run_setup=setup))

    def test_run_bulk_executor_exception(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setting={"generate_error": "yes"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertFalse(generator.run_bulk_executor(bulk_list=[[1,2]],
                                    executor_list=[[1,1]],
                                    run_setup=setup))

    def test_run_bulk_executor_helpers(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list= BundleHelper.ROW_1_COL_10_100,
                                    executor_list=ExecutorHelper.PROCESS_1_8_THREAD_1,
                                    run_setup=setup))

    def test_run_bulk_executor_grow(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2]],
                                    executor_list=ExecutorHelper.grow_thread(process=1, thread_pow_start=1, thread_pow_stop=3),
                                    run_setup=setup))

        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                    executor_list=ExecutorHelper.grow_process(thread=1, process_pow_start=1, process_pow_stop=3),
                                    run_setup=setup))

    def test_run_bulk_executor_initcall(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_PERF_ADR,"perf_gil_impact_test.txt"),
                                     init_call=InitCallSetting.all())

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2], [1,10]],
                                    executor_list=[[1,1], [1,2], [2,2]],
                                    run_setup=setup))

    def test_run_stress_test(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=None)

        setup=RunSetup(duration_second=15, start_delay=0)
        self.assertTrue(generator.run(4, 8, setup))

    def test_run_init_call(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=None,
                                     init_call=InitCallSetting.all())

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertTrue(generator.run(1, 2, setup))


# if __name__ == '__main__':
#     unittest.main()
