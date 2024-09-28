import unittest
import time
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup


class SimulateProbe(ParallelProbe):

    def __init__(self):
        setup = RunSetup(0, 0, {})
        setup.set_start_time()
        super().__init__(setup)

    def run(self, duration_second: list[float] = []):
        
        for duration in duration_second:
            self._core_calc(duration)
        self._core_close()


class TestCasePerf(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_basic_statistic(self):
        simulate=SimulateProbe()

        simulate.run([0.24, 0.21, 0.34, 0.33])


