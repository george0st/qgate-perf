import unittest
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.helper import Helper
from qgate_perf.output_setup import OutputSetup
import time
from os import path
import shutil

def prf_gil_impact(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    # init (contain executor synchronization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

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
    return probe

class TestCasePerf(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCasePerf.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_null_function_exception(self):
        generator = ParallelExecutor(None,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        self.assertFalse(generator.one_run().state)

    def test_one_run(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        self.assertTrue(generator.one_run().state)

    def test_one_run_param(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting={"aa":10,
               "name": "Adam"}

        self.assertTrue(generator.one_run(RunSetup(parameters=setting)).state)

    def test_init_run(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting={"aa":10,
               "name": "Adam"}

        self.assertTrue(generator.init_run(RunSetup(parameters=setting)))
        self.assertTrue(generator.init_run())

    def test_testrun_exception(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting={"generate_error": "yes"}

        # expected False (exception) because "generate_error"
        self.assertFalse(generator.test_run(RunSetup(parameters=setting),print_output=True))

    def test_testrun(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        self.assertTrue(generator.test_run(print_output=True))

    def test_testrun_setup(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting = {"aa": 10,
                   "name": "Adam"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertTrue(generator.test_run(run_setup=setup, print_output=True))

    def test_run(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=4, start_delay=4)
        self.assertTrue(generator.run(2, 2, setup).state)

    def test_run_exception(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run(2, 2, setup).state)

    def test_run_executor(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=4, start_delay=2)
        self.assertTrue(generator.run_executor([[1,1], [2,2]], setup).state)

    def test_run_executor_exception(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertFalse(generator.run_executor([[1,1]], setup).state)

    def test_run_bulk_executor(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"),
                                     init_each_bulk=True)

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2], [1,10]],
                                    executor_list=[[1,1], [2,2]],
                                    run_setup=setup).state)

    def test_run_bulk_executor_exception(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setting={"generate_error": "yes"}

        setup=RunSetup(duration_second=0, start_delay=0, parameters=setting)
        self.assertFalse(generator.run_bulk_executor(bulk_list=[[1,2]],
                                    executor_list=[[1,1]],
                                    run_setup=setup).state)

    def test_run_bulk_executor_helpers(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list= [[1, 10], [1, 50], [1, 100]],
                                    executor_list=[[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread']],
                                    run_setup=setup).state)

    def test_run_bulk_executor_grow(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2]],
                                                    executor_list=Helper.grow_thread(process=1, thread_pow_start=1, thread_pow_stop=3),
                                                    run_setup=setup).state)

        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,1]],
                                                    executor_list=Helper.grow_process(thread=1, process_pow_start=1, process_pow_stop=3),
                                                    run_setup=setup).state)

    def test_run_bulk_executor_initcall(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"),
                                     init_each_bulk=True)

        setup=RunSetup(duration_second=1, start_delay=0)
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,2], [1,10]],
                                    executor_list=[[1,1], [1,2], [2,2]],
                                    run_setup=setup).state)

    def test_run_stress_test(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=None)

        setup=RunSetup(duration_second=15, start_delay=0)
        self.assertTrue(generator.run(4, 8, setup).state)

    def test_run_init_call(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=None,
                                     init_each_bulk=True)

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertTrue(generator.run(1, 2, setup).state)

    def test_general_exception(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="*&%$.txt")

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertFalse(generator.run(1, 2, setup).state)

    def test_general_exception2(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="*&%$.txt")

        setup=RunSetup(duration_second=0, start_delay=0)
        self.assertFalse(generator.run_executor([[1,1]], setup).state)

    def test_output_precision(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup=RunSetup(duration_second=4, start_delay=4)
        OutputSetup().human_precision = 7
        self.assertTrue(generator.run(2, 2, setup).state)
        OutputSetup().human_precision = OutputSetup.HUMAN_PRECISION

    def test_output_json_separator(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_test.txt"))

        setup = RunSetup(duration_second=4, start_delay=4)
        OutputSetup().human_json_separator = (' - ', '::')
        self.assertTrue(generator.run(2, 2, setup).state)
        OutputSetup().human_json_separator = OutputSetup.HUMAN_JSON_SEPARATOR

    def test_run_percentiles(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_percentile.txt"),
                                     init_each_bulk=True)


        setup=RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.90})
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,10]],
                                    executor_list=[[4,1]],
                                    run_setup=setup).state)

    def test_run_percentiles2(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_percentile.txt"),
                                     init_each_bulk=True)


        setup=RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.95})
        self.assertTrue(generator.run_bulk_executor(bulk_list=[[1,10]],
                                    executor_list=[[4,2]],
                                    run_setup=setup).state)

    def test_run_percentiles_only_exceptions(self):
        """Simulate percentile support with bundle execution and all exceptions"""
        generator = ParallelExecutor(prf_gil_impact,
                                     label="percentiles_only_exception",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_percentiles_only_exception.txt"),
                                     init_each_bulk=True)

        setup=RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.95, "generate_error": "yes"})
        generator.run_bulk_executor(bulk_list=[[1,10]],
                                    executor_list=[[1,1], [2,1], [4,2]],
                                    run_setup=setup)
        self.assertTrue(len(generator.create_graph_perf(self.OUTPUT_ADR)) == 1)

    def test_run_performance_detail(self):
        generator = ParallelExecutor(prf_gil_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_gil_impact_percentile.txt"),
                                     init_each_bulk=True)


        setup=RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.95})
        detail = generator.run_bulk_executor(bulk_list=[[1,10], [1,15]],
                                    executor_list=[[1,1], [4,2]],
                                    run_setup=setup,
                                    performance_detail=True)

        self.assertTrue(detail.state)
        self.assertTrue(detail[0][1].call_per_sec > 0)
        self.assertTrue(detail[1][1].call_per_sec > 0)
        self.assertTrue(detail[2][1].call_per_sec > 0)
        self.assertTrue(detail[3][1].call_per_sec > 0)
        self.assertTrue(detail[0][0.95].call_per_sec > 0)
        self.assertTrue(detail[1][0.95].call_per_sec > 0)
        self.assertTrue(detail[2][0.95].call_per_sec > 0)
        self.assertTrue(detail[3][0.95].call_per_sec > 0)
        self.assertTrue(len(str(detail))>0)

        print(str(detail))

# if __name__ == '__main__':
#     unittest.main()
