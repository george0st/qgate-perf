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
        parameters={}
        parameters["percentile"] = percentile
        parameters["heap_init_size"] = heap_init_size

        setup = RunSetup(0, 0, parameters)
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

        # force the END
        self.stop(-1)

        # TODO: add logic

    def check(self, duration_second: list[float] = [], results: list[PercentileItem] = []):

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

    def check2(self, duration_second: list[float] = [], percentiles: list[int] = [], sequences: list[[]] = [[]]):

        items = []
        for i in range(len(percentiles)):
            items.append(PercentileItem(percentiles[i],
                           len(sequences[i]),
                           sum(sequences[i]),
                           std(sequences[i]),
                           min(sequences[i]),
                           max(sequences[i])))

        return self.check(duration_second, items)

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

        simulate = SimulateProbe(50, 10)
        sequence = [0.24, 0.21, 0.34, 0.33]
        lower_sequence = [0.24, 0.21]

        result = simulate.check(sequence,
                       [PercentileItem(0.5,
                                       len(lower_sequence),
                                       sum(lower_sequence),
                                       std(lower_sequence),
                                       min(lower_sequence),
                                       max(lower_sequence)),
                        PercentileItem(1,
                                       len(sequence),
                                       sum(sequence),
                                       std(sequence),
                                       min(sequence),
                                       max(sequence))])
        self.assertIsNone(result, result)

    def test_basic2(self):

        simulate = SimulateProbe(70, 10)
        sequence = [0.24, 0.21, 0.34, 0.33, 0.11, 0.25, 0.10]
        lower_sequence = [0.21, 0.24, 0.10, 0.11]

        result = simulate.check(sequence,
                                [PercentileItem(0.7,
                                                len(lower_sequence),
                                                sum(lower_sequence),
                                                std(lower_sequence),
                                                min(lower_sequence),
                                                max(lower_sequence)),
                                 PercentileItem(1,
                                                len(sequence),
                                                sum(sequence),
                                                std(sequence),
                                                min(sequence),
                                                max(sequence))])
        self.assertIsNone(result, result)

    def test_basic3(self):
        simulate = SimulateProbe(50, 10)
        sequence = [0.24, 0.21, 0.34, 0.33]
        lower_sequence = [0.24, 0.21]

        result = simulate.check2(sequence,
                                 [0.5, 1],
                                 [lower_sequence, sequence])
        self.assertIsNone(result, result)
