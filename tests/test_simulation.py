import heapq
import unittest
import time
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
import numpy as np
from numpy import random

class PercentilHeap():

    def __init__(self, process_fn, percentile = 99):
        self._count = 0
        self._reserve = 2
        self._sequence = [-1] * self._reserve
        self._percentile = percentile
        self._process_fn = process_fn

    def call(self, itm):
        self._count += 1

        if (self._count % self._percentile) == 0:
            expected_size = ((self._count + 1) * self._percentile / 100)
            if (expected_size + self._reserve) > len(self._sequence):
                # extend heap and push value
                heapq.heappush(self._sequence, itm)
                return

        # add item to heap
        if itm >= self._sequence[0]:
            old_itm = heapq.heapreplace(self._sequence, itm)
            print(old_itm)
            # TODO: processing old_itm

    def close(self):
        # identification, how many value must be pop form 99p
        requested_size = self._count - ((self._count + 1) * self._percentile / 100)
        if requested_size > 1:
            pop_operation = int(len(self._sequence) - requested_size)
        else:
            pop_operation = len(self._sequence)

        # free addition values till requested percentile
        for a in range(pop_operation):
            print(heapq.heappop(self._sequence))
            # TODO: processing return value
        print("DONE requested percentile")

        for b in range(len(self._sequence)):
            print(heapq.heappop(self._sequence))
            # TODO: processing return value
        print("DONE all (100p)")


class SimulateProbe(ParallelProbe):

    def __init__(self):
        setup = RunSetup(0, 0, {})
        setup.set_start_time()
        super().__init__(setup)

    def run(self, duration_second: list[float] = []):

        for duration in duration_second:
            self._core_calc(duration)
        self._core_close()

def get_rng_generator(complex_init = True) -> random._generator.Generator:
    """Create generator of random values with initiation"""

    # now and now_ms (as detail about milliseconds)
    now = time.time()
    now_ms = (now - int(now)) * 1000000000

    # calc based on CPU speed
    ns_start = time.perf_counter_ns()
    if complex_init:
        time.sleep(0.01)
        ns_stop = time.perf_counter_ns()

        # create generator with more random seed (now, now_ms, cpu speed)
        return random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])
    else:
        return random.default_rng([int(now), int(now_ms), ns_start])


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
        generator = get_rng_generator()
        sequence = generator.integers(0, 100,10) / 100

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic2(self):
        generator = get_rng_generator()
        sequence = generator.integers(0, 1000,50) / 100

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_random_statistic3(self):
        generator = get_rng_generator()
        sequence = generator.integers(0, 10000,100) / 100

        simulate=SimulateProbe()
        simulate.run(sequence)
        self._check(simulate, sequence)

    def test_percentile(self):
        # https://www.geeksforgeeks.org/max-heap-in-python/
        #https://www.datova-akademie.cz/slovnik-pojmu/percentil/
        #https://github.com/sengelha/streaming-percentiles

        from heapq import heappop, heappush, heapify

        reserve = 2
        # Creating empty heap
        sequence = [-1] * reserve

        generator = get_rng_generator()

        for count in range(1, 17000):
            itm = generator.integers( 0, 500)/10000
            if (count % 100) == 0:
                one_percent = ((count + 1) / 100)
                if (one_percent + reserve) > len(sequence):
                    heapq.heappush(sequence, itm)
                    continue

            if itm >= sequence[0]:
                print(heapq.heapreplace(sequence, itm))
                # TODO: processing return value
        print("size:", len(sequence))

        # identification, how many value must be pop form 99p
        if count > 99:
            requested_size = count - ((count + 1) * 99 / 100)
            pop_operation = int(len(sequence) - requested_size)
        else:
            pop_operation = len(sequence)

        # free addition values till 99 percentile
        for a in range(pop_operation):
            print(heapq.heappop(sequence))
            # TODO: processing return value
        print("DONE 99p")

        for b in range(len(sequence)):
            print(heapq.heappop(sequence))
            # TODO: processing return value
        print("DONE 100p")

    def test_percentile1(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.56, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12,
                    0.24, 0.21, 0.34, 0.33, 0.11, 0.22, 0.33, 0.23, 0.21, 0.12]


#https://www.datova-akademie.cz/slovnik-pojmu/percentil/
#https://github.com/sengelha/streaming-percentiles