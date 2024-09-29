import heapq
import unittest
import time
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
import numpy as np
from numpy import random


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

        size = 128
        # Creating empty heap
        sequence = [-1] * size

        generator = get_rng_generator()

        for i in range(1, 1000):
            itm = generator.integers( 0, 500)/10000
            one_percent = (i+1) / 100
            if one_percent > size:
#                if itm >= sequence[0]:
                size +=1
                heapq.heappush(sequence, itm)
                continue

            if itm >= sequence[0]:
                print(heapq.heapreplace(sequence, itm))
                # work with return value
        print("size:",size)

        if i > 99:
            requested_size = i - ((i + 1) * 99 / 100)
            pop_operation = int(len(sequence) - requested_size)
        else:
            pop_operation = len(sequence)

        # free addition values till 99 percentile
        for a in range(pop_operation):
            print(heapq.heappop(sequence))
        print("DONE 99p")

        for b in range(len(sequence)):
            print(heapq.heappop(sequence))
        print("DONE 100p")
        # for i in range(500):
        #     itm = generator.integers(-1000, 0)
        #     heapq.heapreplace(sequence, itm)
        #     print(str(-1*sequence[0]))


        # sequence = [-0.24, -0.21, -0.34, -0.33, -0.345, -0.11, -0.232435, -0.2344, -1.4, -2.455]
        # heapify(sequence)
        #
        # # # printing the value of maximum element
        # # print("Head value of heap : " + str(-1 * sequence[0]))
        #
        # print(str(-1*heappop(sequence)))
        # heappush(sequence, -1)
        # print(str(-1*heappop(sequence)))
        # heappush(sequence, -19)
        # print(str(-1*heappop(sequence)))
        # print(str(-1*heapq.heapreplace(sequence, -0.5)))
        # print(str(-1*heapq.heapreplace(sequence, -0.5)))
        # print(str(-1*heapq.heapreplace(sequence, -0.5)))

        # # importing "heapq" to implement heap queue
        # import heapq
        #
        # # initializing list
        # li = [5, 7, 9, 1, 3]
        #
        # # using heapify to convert list into heap
        # heapq.heapify(li)
        #
        # # printing created heap
        # print("The created heap is : ", (list(li)))
        #

        # sequence = [0.24, 0.21, 0.34, 0.33, 0.345, 0.11, 0.232435, 0.2344, 1.4, 2.455]
        # percentile50 =
        # for itm in sequence:


#https://www.datova-akademie.cz/slovnik-pojmu/percentil/
#https://github.com/sengelha/streaming-percentiles