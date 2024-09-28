import unittest
import time
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
import numpy as np


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

    def _check(self, simulate, sequence):
        """Check value from ParallelProbe vs calc from Numpy"""
        expected ={}
        expected['call'] = len(sequence)
        expected['avr'] = float(round(np.average(sequence), ParallelProbe.HUMAN_PRECISION))
        expected['min'] = float(np.min(sequence))
        expected['max'] = float(np.max(sequence))
        expected['std'] = float(round(np.std(sequence), ParallelProbe.HUMAN_PRECISION))
        expected['total'] = float(round(np.sum(sequence),ParallelProbe.HUMAN_PRECISION))

        print("Parallel probe    :", simulate.readable_str())
        print("Numpy calculation :", str(expected))

        self.assertTrue(simulate.counter == expected['call'])
        self.assertTrue(round(simulate.total_duration / simulate.counter, ParallelProbe.HUMAN_PRECISION) == expected['avr'])
        self.assertTrue(simulate.min_duration == expected['min'])
        self.assertTrue(simulate.max_duration == expected['max'])
        self.assertTrue(round(simulate.standard_deviation,ParallelProbe.HUMAN_PRECISION) == expected['std'])
        self.assertTrue(round(simulate.total_duration, ParallelProbe.HUMAN_PRECISION) == expected['total'])


    def test_basic_statistic(self):
        sequence = [0.24, 0.21, 0.34, 0.33]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)