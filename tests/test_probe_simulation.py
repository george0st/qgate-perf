import unittest
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.output_setup import OutputSetup
from qgate_perf.executor_helper import get_rng_generator
import numpy as np


class SimulateProbe(ParallelProbe):

    def __init__(self):
        setup = RunSetup(0, 0, {})
        setup.set_start_time()
        super().__init__(setup)

    def start(self):
        pass

    def stop(self, duration_one_shot):
        if duration_one_shot >=0:
            self.heap.call(duration_one_shot)
            #self._core_calc(duration_one_shot)

        # Is it possible to end performance testing?
        if duration_one_shot == -1:
            self.heap.close()
            #self._core_close()
            return True
        return False

    def run(self, duration_second: list[float] = []):

        for duration_one_shot in duration_second:
            self.start()
            self.stop(duration_one_shot)

        # TODO: add logic

class TestCaseProbeSimulate(unittest.TestCase):
    """Simulate performance input for calculation of call, min, max, avr, std, total."""

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_basic1(self):
        sequence = [0.24, 0.21, 0.34, 0.33, -1]

        simulate = SimulateProbe()
        simulate.run(sequence)
        #self._check(simulate, sequence)
