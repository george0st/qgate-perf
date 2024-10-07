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

    def run(self, duration_second: list[float] = []):

        for duration in duration_second:
            self._core_calc(duration)
        self._core_close()

class TestCaseSimulate(unittest.TestCase):
    """Simulate processing of input from performance tests"""

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def _check(self, simulate, sequence):
        """Check value from ParallelProbe vs calc from Numpy"""
        expected = {}
        expected['call'] = len(sequence)
        expected['avr'] = float(round(np.average(sequence), OutputSetup().human_precision))
        expected['min'] = float(round(np.min(sequence), OutputSetup().human_precision))
        expected['max'] = float(round(np.max(sequence), OutputSetup().human_precision))
        expected['std'] = float(round(np.std(sequence), OutputSetup().human_precision))
        expected['total'] = float(round(np.sum(sequence), OutputSetup().human_precision))

        print("Parallel probe    :", simulate.readable_str(False))
        print("Numpy calculation :", str(expected))

        self.assertTrue(simulate.counter == expected['call'])
        self.assertTrue(round(simulate.total_duration / simulate.counter, OutputSetup().human_precision) == expected['avr'])
        self.assertTrue(round(simulate.min_duration, OutputSetup().human_precision) == expected['min'])
        self.assertTrue(round(simulate.max_duration, OutputSetup().human_precision) == expected['max'])
        self.assertTrue(round(simulate.standard_deviation, OutputSetup().human_precision) == expected['std'])
        self.assertTrue(round(simulate.total_duration, OutputSetup().human_precision) == expected['total'])

    def test_basic_statistic1(self):
        sequence = [0.24, 0.21, 0.34, 0.33]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic2(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic3(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic4(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic5(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332, 7.334, 3.454, 7.3333, 0.3344, 0.576565, 0.8787]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_basic_statistic6(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455, 88, 99, 1995, 334, 222, 4.33,
                    0.222, 0.2323, 0.456, 0.545, 0.332, 7.334, 3.454, 7.3333, 0.3344, 0.576565, 0.8787, 1.1, 1.1, 1.4,
                    1.3, 1.5, 3.2, 0.44]

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic1(self):
        generator = get_rng_generator()
        sequence = generator.integers(0, 100,10) / 100

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic2(self):
        generator = get_rng_generator()
        sequence = generator.integers(0, 1000,50) / 100

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic3(self):
        generator = get_rng_generator()
        sequence = generator.integers(0, 10000,100) / 100

        simulate = SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

