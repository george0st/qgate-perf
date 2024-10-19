from qgate_perf.parallel_probe import PercentileSummary


class PerfResult:
    """Outputs from performance tests"""

    def __init__(self, row, col, process, thread, percentile_list: dict[PercentileSummary]):

        self.bundle_row = row
        self.bundle_col = col

        self.executor_process = process
        self.executor_thread = thread

        self._percentile_list = percentile_list

    @property
    def percentiles(self) -> dict[PercentileSummary]:
        return self._percentile_list

    @percentiles.setter
    def percentiles(self, value):
        self._percentile_list = value

    def __getitem__(self, key) -> PercentileSummary:
        return self._percentile_list[key]

    def __len__(self):
        return len(self._percentile_list)

    def __str__(self):
        return (f"bundle ({self.bundle_row}x{self.bundle_col}), executor ({self.executor_process}x{self.executor_thread})"
                f" = {self.percentile[0].call_per_sec}")


class PerfResults(list):

    def __init__(self):
        self._results = []

    def append(self, item):

        if isinstance(item, PerfResult):
            self._results.append(item)

        if isinstance(item, PerfResults):
            for itm in item._results:
                self._results.append(itm)

    def __getitem__(self, index) -> PerfResult:
        return self._results[index]

    def __len__(self):
        return len(self._results)

    def __str__(self):
        pass

