from qgate_perf.parallel_probe import PercentileSummary


class OutputPerformance:
    """Outputs from performance tests"""

#    def __init__(self, row, col, process, thread, calls_sec_raw, calls_sec):
    def __init__(self, row, col, process, thread, percentile_list: dict[PercentileSummary]):

        self.bundle_row = row
        self.bundle_col = col

        self.executor_process = process
        self.executor_thread = thread

        self.percentile_list = percentile_list

        # self.calls_sec_raw = calls_sec_raw
        # self.calls_sec = calls_sec


    @property
    def percentiles(self) -> dict[PercentileSummary]:
        return self.percentile_list

    @percentiles.setter
    def percentiles(self, value):
        self.percentile_list = value

    def __str__(self):
        return (f"bundle ({self.bundle_row}x{self.bundle_col}), executor ({self.executor_process}x{self.executor_thread})"
                f" = {self.percentile[0].call_per_sec}")
