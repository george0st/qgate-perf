import math
import unittest
from qgate_perf.percentile_heap import PercentileHeap


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

    def _simulate_close_fn(self, percentile):
        if percentile == self._percentile:
            self._simulate_open = False
            print("Requested percentile: ", self._percentile)
        elif percentile == 1:
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
                print(f"Unexpected value '{itm}' in collection")
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
        heap = SimulatePercentileHeap(0.5)
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
        heap = SimulatePercentileHeap(0.7)
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
        heap = SimulatePercentileHeap(0.9)
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
        heap = SimulatePercentileHeap(0.95)
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
        heap = SimulatePercentileHeap(0.99)
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



