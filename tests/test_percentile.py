import heapq
import math
import unittest

import numpy as np

from qgate_perf.executor_helper import get_rng_generator


class PercentileHeap():

    # https://www.geeksforgeeks.org/max-heap-in-python/
    # https://www.datova-akademie.cz/slovnik-pojmu/percentil/
    # https://github.com/sengelha/streaming-percentiles

    def __init__(self, call_fn, close_fn, percentile = 99, init_size = 10):
        """
        The keep in the heap values above requested percentile

        :param call_fn:         function for standard processing value
        :param close_fn:        function for close processing
        :param percentile:      requested percentile (smaller value will affect bigger memory allocation),
                                recommendation is to use 99 or 95 (99 is default)
        """
        self._init_size = init_size
        self._percentile = percentile / 100
        self._call_fn = call_fn
        self._close_fn = close_fn
        self._clean()

    def _clean(self):
        """Clean heap to the init value"""
        self._count = 0
        self._sequence = [-1] * self._init_size

    def call(self, itm):
        """
        Function push value to the heap and also pop valid value for processing (via call_fn).

        :param itm:     item for precessing
        """
        self._count += 1

        perc = (self._count + 1) * self._percentile
        if perc < self._count:
            requested_size = 1 + math.ceil(self._count - perc)
            if requested_size > len(self._sequence):
                # extend heap and only push value
                heapq.heappush(self._sequence, itm)
                return

        # add item to heap
        if itm >= self._sequence[0]:
            old_itm = heapq.heapreplace(self._sequence, itm)
            if old_itm >= 0:                # remove items with init value '-1'
                self._call_fn(old_itm)
        else:
            self._call_fn(itm)

    def close(self):
        """
        The close processing, will be caller function call_fn and close_fn
        """

        # identification, how many values must be pop form 99p
        requested_size = self._count - ((self._count + 1) * self._percentile)
        requested_size_max = math.ceil(requested_size)
        if requested_size_max >= 1:
            pop_operation = int(len(self._sequence) - requested_size)
        else:
            pop_operation = len(self._sequence)

        # free addition values till requested percentile
        for a in range(pop_operation):
            itm = heapq.heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        self._close_fn()

        for b in range(len(self._sequence)):
            itm = heapq.heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        self._close_fn()
        self._clean()

class SimulatePercentileHeap(PercentileHeap):

    def __init__(self, percentile = 99, init_size = 2):
        super().__init__(self._simulate_call_fn, self._simulate_close_fn, percentile, init_size)
        self._simulate_buffer = []
        self._simulate_buffer_full = []
        self._simulate_open = True

    def _simulate_call_fn(self, itm):
        if self._simulate_open:
            self._simulate_buffer.append(itm)
        self._simulate_buffer_full.append(itm)
        print("Call: ", itm)

    def _simulate_close_fn(self):
        if self._simulate_open:
            self._simulate_open = False
            print("Requested percentile: ", self._percentile)
        else:
            print("DONE all (100p)")

    def test(self, sequence: list, percentile_list_size: int, percentile_out_of_list: list) -> bool:
        result = False

        self.clean()
        for itm in sequence:
            self.call(itm)
        self.close()
        result = self._check(sequence, percentile_list_size, percentile_out_of_list)
        print("----------------")
        return result

    def _check(self, sequence: list, percentile_list_size: int, percentile_out_of_list: list):

        print(f"=> Amount: {len(sequence)},",
              f"Percentile: {(len(sequence)+1)*self._percentile},",
              f"Keep: {len(sequence) - math.floor((len(sequence)+1)*self._percentile)},",
              f"Sequence: {sequence} <=")

        # check size of complete/full collection
        if len(self._simulate_buffer_full) != len(sequence):
            print("Unexpected size of full collection")
            return False

        # check size of collection by percentile
        if len(self._simulate_buffer) != percentile_list_size:
            print("Unexpected size of collection")
            return False

        # check missing values
        for itm in percentile_out_of_list:
            if itm in self._simulate_buffer:
                print(f"Unexpected valie '{itm}' in collection")
                return False
        return True

    def clean(self):
        self._simulate_buffer = []
        self._simulate_buffer_full = []
        self._simulate_open = True
        super()._clean()

class TestCasePercentile(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_percentile50(self):
        heap = SimulatePercentileHeap(50)
        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21],
                                   4,
                                   [0.33, 0.34, 0.24]))

        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11],
                                   3,
                                   [0.33, 0.34]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.21, 0.33],
                                   3,
                                   [0.33, 0.34]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.21],
                                   2,
                                   [0.33, 0.24]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11],
                                   2,
                                   [0.34]))

        self.assertTrue(heap.test([0.34, 0.24],
                                  1,
                                  [0.34]))

        self.assertTrue(heap.test([0.34],
                                  1,
                                  []))

    def test_percentile70(self):
        heap = SimulatePercentileHeap(70)
        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21],
                                  6,
                                  [0.34, 0.55]))

        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21],
                                  5,
                                  [0.33, 0.34]))

        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11],
                                  4,
                                  [0.34]))

        self.assertTrue(heap.test([0.11, 0.21, 0.24, 0.33, 0.34],
                                  4,
                                  [0.34]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.21, 0.33],
                                  4,
                                  [0.34]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.33],
                                  3,
                                  [0.34]))

        self.assertTrue(heap.test([0.34, 0.24, 0.11],
                                  2,
                                  [0.34]))

        self.assertTrue(heap.test([0.34, 0.24],
                                  2,
                                  []))

        self.assertTrue(heap.test([0.34],
                                  1,
                                  []))

    def test_percentile90(self):
        heap = SimulatePercentileHeap(90)
        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  9,
                                  [0.55]))

        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10],
                                  9,
                                  []))

        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21],
                                  8,
                                  []))

        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21],
                                  7,
                                  []))

        self.assertTrue(heap.test([0.24, 0.21, 0.34, 0.33, 0.11],
                                  5,
                                  []))

        self.assertTrue(heap.test([0.11, 0.21, 0.24, 0.33, 0.34],
                                  5,
                                  []))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.21, 0.33],
                                  5,
                                  []))

        self.assertTrue(heap.test([0.34, 0.24, 0.11, 0.33],
                                  4,
                                  []))

        self.assertTrue(heap.test([0.34, 0.24, 0.11],
                                  3,
                                  []))

        self.assertTrue(heap.test([0.34, 0.24],
                                  2,
                                  []))

        self.assertTrue(heap.test([0.34],
                                  1,
                                  []))

    def test_percentile95(self):
        heap = SimulatePercentileHeap(95)
        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.53, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.52, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  38,
                                  [0.54, 0.55]))

        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.53, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  29,
                                  [0.55]))

        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  19,
                                  [0.55]))

        self.assertTrue(heap.test([0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  10,
                                  []))

    def test_percentile99(self):
        heap = SimulatePercentileHeap(99)
        self.assertTrue(heap.test([0.59, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.58, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.57, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.56, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.53, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.52, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.51, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.50, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.49, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  109,
                                  [0.59]))

        self.assertTrue(heap.test([0.59, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.58, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.57, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.56, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.53, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.52, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.51, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.50, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  99,
                                  [0.59]))

        self.assertTrue(heap.test([0.59, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.58, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.57, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.56, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.55, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.54, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.53, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.52, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10,
                                   0.51, 0.24, 0.21, 0.34, 0.33, 0.11, 0.23, 0.21, 0.10, 0.10],
                                  90,
                                  []))



