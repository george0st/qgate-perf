import heapq
import math
import unittest
from qgate_perf.executor_helper import get_rng_generator


class PercentilHeap():

    # https://www.geeksforgeeks.org/max-heap-in-python/
    # https://www.datova-akademie.cz/slovnik-pojmu/percentil/
    # https://github.com/sengelha/streaming-percentiles

    def __init__(self, call_fn, close_fn, percentile = 99):
        """
        The keep in the heap values above requested percentile

        :param call_fn:         function for standard processing value
        :param close_fn:        function for close processing
        :param percentile:      requested percentile (smaller value will affect bigger memory allocation),
                                recommendation is to use 99 or 95 (99 is default)
        """
        self._count = 0
        self._init_size = 2
        self._sequence = [-1] * self._init_size
        self._percentile = percentile / 100
        self._call_fn = call_fn
        self._close_fn = close_fn

    def call(self, itm):
        """
        Function push value to the heap and also pop valid value for processing (via call_fn).

        :param itm:     item for precessing
        """
        self._count += 1

        perc = (self._count + 1) * self._percentile
        if perc < self._count:
            requested_size = self._count - perc
            requested_size = 1 + math.ceil(requested_size)
            if requested_size > len(self._sequence):
                # extend heap and only push value
                heapq.heappush(self._sequence, itm)
                return

#        if perc >= 1 and perc <= self._count:


        # add item to heap
        if itm >= self._sequence[0]:
            old_itm = heapq.heapreplace(self._sequence, itm)
            if old_itm >= 0:
                self._call_fn(old_itm)
        else:
            self._call_fn(itm)

    def close(self):
        """
        The close processing, will be caller function call_fn and close_fn
        """
        # identification, how many value must be pop form 99p
        perc = (self._count + 1) * self._percentile
        requested_size = 1 + (self._count - math.floor(perc))
        if requested_size >= 1:
            pop_operation = int(len(self._sequence) - requested_size)
        else:
            pop_operation = len(self._sequence)

        # free addition values till requested percentile
        for a in range(pop_operation):
            itm = heapq.heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        print("DONE requested percentile")
        self._close_fn(99)

        for b in range(len(self._sequence)):
            itm = heapq.heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        print("DONE all (100p)")
        self._close_fn(100)

class TestCasePercentile(unittest.TestCase):

    OUTPUT_ADR = "../output/test_perf/"
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


    def test_percentile1(self):
        sequence = [0.24, 0.21, 0.34, 0.33, 0.11]
        heap = PercentilHeap(self.my_call_fn, self.my_close_fn, 70)

        for itm in sequence:
            heap.call(itm)
        heap.close()

    def my_call_fn(self, itm):
        print("Processing:", itm)

    def my_close_fn(self, itm):
        print("Close")

    def test_percentile2(self):
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

