import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_return import ParallelReturn
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
import time


def prf_GIL_impact(return_key, return_dict, run_setup: RunSetup):
    """ Function for performance testing"""
    try:
        # init (contain executor synchonization, if needed)
        performance = ParallelReturn(run_setup)

        while (True):

            # START - performance measure for specific part of code
            performance.start()

            for r in range(run_setup.bulk_row * run_setup.bulk_col):
                time.sleep(0)

            # STOP - performance measure specific part of code
            if performance.stop():
                break

        # return outputs
        if return_dict is not None:
            return_dict[return_key] = performance

    except Exception as ex:
        # return outputs in case of error
        if return_dict is not None:
            return_dict[return_key] = ParallelReturn(None, ex)

class MyTestCase(unittest.TestCase):
    def test_one_shot(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="../output/test_gil_impact_test.txt")

        generator.one_shot()

    def test_run(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="../output/test_gil_impact_test.txt")

        setup=RunSetup(duration_second=5, start_delay=0)
        generator.run(2, 2, setup)

    def test_run_executor(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="../output/test_gil_impact_test.txt")

        setup=RunSetup(duration_second=1, start_delay=0)
        generator.run_executor([[1,1], [1,2], [2,2]], setup)

    def test_run_bulk_executor(self):
        generator = ParallelExecutor(prf_GIL_impact,
                                     label="GIL_impact",
                                     detail_output=True,
                                     output_file="../output/test_gil_impact_test.txt")

        setup=RunSetup(duration_second=1, start_delay=0)
        generator.run_bulk_executor(bulk_list=[[1,1], [1,10], [1,100]],
                                    executor_list=[[1,1], [1,2], [2,2]],
                                    run_setup=setup)


if __name__ == '__main__':
    unittest.main()
