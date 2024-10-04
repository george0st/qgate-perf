
class OutputPerformance:
    """Outputs from performance tests"""

    def __init__(self, row, col, process, thread, calls_sec):

        self.bundle_row = row
        self.bundle_col = col

        self.executor_process = process
        self.executor_thread = thread

        self.calls_sec = calls_sec

    def __str__(self):
        return f"bundle ({self.bundle_row}x{self.bundle_col}), executor ({self.executor_process}x{self.executor_thread}) = {self.calls_sec}"
