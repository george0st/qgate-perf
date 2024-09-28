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
        expected['min'] = float(round(np.min(sequence), ParallelProbe.HUMAN_PRECISION))
        expected['max'] = float(round(np.max(sequence), ParallelProbe.HUMAN_PRECISION))
        expected['std'] = float(round(np.std(sequence), ParallelProbe.HUMAN_PRECISION))
        expected['total'] = float(round(np.sum(sequence),ParallelProbe.HUMAN_PRECISION))

        print("Parallel probe    :", simulate.readable_str())
        print("Numpy calculation :", str(expected))

        self.assertTrue(simulate.counter == expected['call'])
        self.assertTrue(round(simulate.total_duration / simulate.counter, ParallelProbe.HUMAN_PRECISION) == expected['avr'])
        self.assertTrue(round(simulate.min_duration, ParallelProbe.HUMAN_PRECISION) == expected['min'])
        self.assertTrue(round(simulate.max_duration, ParallelProbe.HUMAN_PRECISION) == expected['max'])
        self.assertTrue(round(simulate.standard_deviation,ParallelProbe.HUMAN_PRECISION) == expected['std'])
        self.assertTrue(round(simulate.total_duration, ParallelProbe.HUMAN_PRECISION) == expected['total'])


    def test_basic_statistic1(self):
        sequence = [0.24, 0.21, 0.34, 0.33]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic2(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic3(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic4(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic5(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332, 7.334, 3.454, 7.3333, 0.3344, 0.576565, 0.8787]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic6(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332, 7.334, 3.454, 7.3333, 0.3344, 0.576565, 0.8787, 1.1, 1.1, 1.4,
                    1.3, 1.5, 3.2, 0.44]

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic1(self):
        # TODO: Add random sequences, range (0.1 - 0.98)
        pass

    def test_random_statistic2(self):
        # TODO: Add random sequences, range (0.1 - 10)
        pass

    def test_random_statistic3(self):
        # TODO: Add random sequences, range (0.1 - 100)
        pass