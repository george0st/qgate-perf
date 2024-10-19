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


def prf_partly(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing, where measurement is based on
     the piece of code (partly code parts)"""

    # init (contain executor synchronization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

    while (True):

        # partly INIT - performance measurement for
        probe.partly_init()

        # partly START -  partly measurement (part 1.)
        probe.partly_start()
        time.sleep(0.01)
        # partly STOP - partly measurement (part 1.)
        probe.partly_stop()

        time.sleep(2)

        # partly START - partly measurement (part 2.)
        probe.partly_start()
        time.sleep(0.01)
        # partly STOP - partly measurement (part 2.)
        probe.partly_stop()

        time.sleep(2)

        # partly START - partly measurement (part 3.)
        probe.partly_start()
        time.sleep(0.01)
        # partly STOP - partly measurement (part 3.)
        probe.partly_stop()

        # partly FINISH - summary for all partly measurement
        if probe.partly_finish():
            break

    if run_setup.param("generate_error"):
        raise Exception('Simulated error')

    # return outputs
    return probe


class TestCasePerfPartly(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCasePerfPartly.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_basic1(self):
        generator = ParallelExecutor(prf_partly,
                                     label="prf_partly",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_partly.txt"),
                                     init_each_bulk=True)


        setup = RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.90})
        perf = generator.run_bulk_executor(bulk_list=[[1,10]],
                                    executor_list=[[4,1]],
                                    run_setup=setup,
                                    performance_detail=True)

        self.assertTrue(perf.state)
        self.assertTrue(perf[0][1].avrg < 1 and perf[0][0.9].avrg < 1)

    def test_basic2(self):
        generator = ParallelExecutor(prf_partly,
                                     label="prf_partly",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_partly.txt"),
                                     init_each_bulk=True)


        setup = RunSetup(duration_second=1, start_delay=0, parameters={"percentile": 0.90})
        perf = generator.run_bulk_executor(bulk_list=[[1,10]],
                                    executor_list=[[2,1], [4,1]],
                                    run_setup=setup,
                                    performance_detail=True)

        self.assertTrue(perf.state)
        self.assertTrue(perf[0][1].avrg < 1 and perf[0][0.9].avrg < 1)
        self.assertTrue(perf[1][1].avrg < 1 and perf[1][0.9].avrg < 1)
