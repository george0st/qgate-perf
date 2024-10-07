import heapq
import unittest
from qgate_perf.executor_helper import get_rng_generator


class PercentilHeap():

    def __init__(self, call_fn, close_fn, percentile = 99):
        """
        The keep in the heap values above requested percentile

        :param call_fn:         function for standard processing value
        :param close_fn:        function for close processing
        :param percentile:      requested percentile (smaller value will affect bigger memory allocation),
                                recommendation is to use 99 or 95 (99 is default)
        """
        self._count = 0
        self._reserve = 2
        self._sequence = [-1] * self._reserve
        self._percentile = percentile
        self._call_fn = call_fn
        self._close_fn = close_fn

    def call(self, itm):
        """
        Function push value to the heap and also pop valid value for processing (via call_fn).

        :param itm:     item for precessing
        """
        self._count += 1

        if (self._count % self._percentile) == 0:
            expected_size = ((self._count + 1) * self._percentile / 100)
            if (expected_size + self._reserve) > len(self._sequence):
                # extend heap and only push value
                heapq.heappush(self._sequence, itm)
                return

        # add item to heap
        if itm >= self._sequence[0]:
            old_itm = heapq.heapreplace(self._sequence, itm)
            self._call_fn(old_itm)

    def close(self):
        """
        The close processing, will be caller function call_fn and close_fn
        """
        # identification, how many value must be pop form 99p
        requested_size = self._count - ((self._count + 1) * self._percentile / 100)
        if requested_size > 1:
            pop_operation = int(len(self._sequence) - requested_size)
        else:
            pop_operation = len(self._sequence)

        # free addition values till requested percentile
        for a in range(pop_operation):
            itm = heapq.heappop(self._sequence)
            self._call_fn(itm)
        print("DONE requested percentile")
        self._close_fn(99)

        for b in range(len(self._sequence)):
            itm = heapq.heappop(self._sequence)
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