from heapq import heappop, heappush, heapreplace
import math


class PercentileHeap():

    # https://www.geeksforgeeks.org/max-heap-in-python/
    # https://www.datova-akademie.cz/slovnik-pojmu/percentil/
    # https://github.com/sengelha/streaming-percentiles

    def __init__(self, call_fn, close_fn, percentile = 99, heap_init_size = 100):
        """
        The keep in the heap values above requested percentile

        :param call_fn:         function for standard processing value
        :param close_fn:        function for close processing
        :param percentile:      requested percentile (smaller value will affect bigger memory allocation),
                                recommendation is to use 99 or 95 (99 is default)
        :param heap_init_size:  init size for heap (default is 100)
        """
        self._init_size = heap_init_size
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
                heappush(self._sequence, itm)
                return

        # add item to heap
        if itm >= self._sequence[0]:
            old_itm = heapreplace(self._sequence, itm)
            if old_itm >= 0:                # remove items with init value '-1'
                self._call_fn(old_itm)
        else:
            self._call_fn(itm)

    def close(self):
        """
        The close processing, will be caller function call_fn and close_fn
        """

        # free values till requested percentile
        # identification, how many values must be pop for requested percentile
        requested_size = self._count - ((self._count + 1) * self._percentile)
        requested_size_max = math.ceil(requested_size)
        if requested_size_max >= 1:
            pop_operation = int(len(self._sequence) - requested_size)
        else:
            pop_operation = len(self._sequence)

        for a in range(pop_operation):
            itm = heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        self._close_fn(self._percentile)

        # free rest of value for 100 percentile
        for b in range(len(self._sequence)):
            itm = heappop(self._sequence)
            if itm >= 0:
                self._call_fn(itm)
        self._close_fn(1)
        self._clean()
