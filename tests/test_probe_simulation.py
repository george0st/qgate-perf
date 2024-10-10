import math
import unittest
from qgate_perf.parallel_probe import ParallelProbe, PercentileItem
from qgate_perf.run_setup import RunSetup
from numpy import std, sum, min, max
from qgate_perf.output_setup import OutputSetup
from qgate_perf.executor_helper import get_rng_generator
import numpy as np


class SimulateProbe(ParallelProbe):

    MATH_PRECISION = 5

    def __init__(self, percentile, heap_init_size):

        self.percentile = percentile
        self.heap_init_size = heap_init_size

        parameters={}
        parameters["percentile"] = self.percentile
        parameters["heap_init_size"] = self.heap_init_size

        setup = RunSetup(0, 0, parameters)
        setup.set_start_time()
        super().__init__(setup)

    def start(self):
        pass

    def stop(self, duration_one_shot):
        if duration_one_shot >= 0:
            self.heap.call(duration_one_shot)

        # Is it possible to end performance testing?
        if duration_one_shot == -1:
            self.heap.close()
            return True
        return False

    def run(self, duration_second: list[float] = []):

        for duration_one_shot in duration_second:
            self.start()
            self.stop(duration_one_shot)

        # force the END
        self.stop(-1)

        # TODO: add logic

    def _check(self, duration_second: list[float] = [], results: list[PercentileItem] = []):

        # calc outputs
        self.run(duration_second)

        # check expected results
        if len(self.percentile_results) != len(results):
            return "Invalid amount of results"

        for result in results:
            check_result = False
            for percentile_result in self.percentile_results:
                if percentile_result.percentile == result.percentile:
                    if (percentile_result.count == result.count and
                            round(percentile_result.total_duration, SimulateProbe.MATH_PRECISION) == round(result.total_duration, SimulateProbe.MATH_PRECISION) and
                            percentile_result.min == result.min and
                            percentile_result.max == result.max and
                            round(percentile_result.std, SimulateProbe.MATH_PRECISION) == round(result.std, SimulateProbe.MATH_PRECISION)):
                        check_result = True
                    break
            if not check_result:
                return f"Invalid values or missing values for '{result.percentile}' percentile"
        return None

    def check(self, duration_second: list[float] = []): #, percentiles: list[int] = [], sequences: list[[]] = [[]]):

        # create init data
        percentiles = [self.percentile, 1]
        sequences = [self.create_percentile_seq(duration_second), duration_second]

        items = []
        for i in range(len(percentiles)):
            if sequences[i]:
                items.append(PercentileItem(percentiles[i],
                               len(sequences[i]),
                               sum(sequences[i]),
                               std(sequences[i]),
                               min(sequences[i]),
                               max(sequences[i])))
            else:
                items.append(PercentileItem(percentiles[i],
                                            0,
                                            0,
                                            0,
                                            ParallelProbe.MIN_DURATION,
                                            0))
        return self._check(duration_second, items)

    def create_percentile_seq(self, sequence):
        expected_size = int(math.floor((len(sequence) + 1) * self.percentile))
        if expected_size > 0:
            percentile_sequence = sequence.copy()
            percentile_sequence.sort()
            return percentile_sequence[0: expected_size]
        return None

class TestCaseProbeSimulate(unittest.TestCase):
    """Simulate performance input for calculation of call, min, max, avr, std, total."""

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_basic_0_with_exception(self):
        with self.assertRaises(Exception) as context:
            simulate = SimulateProbe(0, 10)

        with self.assertRaises(Exception) as context:
            simulate = SimulateProbe(0, 10)

    def test_basic_10(self):
        simulate = SimulateProbe(0.1, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.1, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_50(self):
        simulate = SimulateProbe(0.5, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.5, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_70(self):
        simulate = SimulateProbe(0.7, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.7, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_90(self):
        simulate = SimulateProbe(0.9, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.9, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_99(self):
        simulate = SimulateProbe(0.99, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.99, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_999(self):
        simulate = SimulateProbe(0.999, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33])
        self.assertIsNone(result, result)

        simulate = SimulateProbe(0.999, 10)
        result = simulate.check([0.24, 0.21, 0.34, 0.33, 0.33, 0.221, 0.23, 0.21, 0.45, 0.76])
        self.assertIsNone(result, result)

    def test_basic_100_with_exception(self):
        with self.assertRaises(Exception) as context:
            simulate = SimulateProbe(1, 10)

        with self.assertRaises(Exception) as context:
            simulate = SimulateProbe(1, 10)
