import datetime

class RunSetup:

    def __init__(self, duration_second, start_delay: int, parameters: dict={}):
        """ Setup of execution

        :param duration_second:     parametrs for duration of atomic execution (it is up to function, if it will reflect the value)
        :param start_delay:         maximal time for waiting/synchronization, before execution of all executors (0 = without synchronization)
        :param parameters:          addition parameters for execution
        """
        self._duration_second=duration_second
        self._bulk_row = 1
        self._bulk_col = 10
        self._start_delay=start_delay
        self._when_start=None

        # collection of specific keys for project such as project_name, feature_set_name, etc.
        self._parameters=parameters

    @property
    def bulk_row(self):
        return self._bulk_row
    @property
    def bulk_col(self):
        return self._bulk_col

    @property
    def when_start(self):
        return self._when_start

    def param(self, key: str):
        """Return key parameter"""
        if self._parameters:
            return self._parameters[key]
        return None

    @property
    def duration_second(self):
        return self._duration_second

    def set_start_time(self):
        """Define unique start time for all executors. The time has to be setup before executor start."""
        self._when_start = datetime.datetime.now() + datetime.timedelta(seconds=self._start_delay)

    def set_bulk(self, bulk_row, bulk_column):
        self._bulk_row = bulk_row if bulk_row > 0 else 1
        self._bulk_col = bulk_column if bulk_column > 0 else 1
