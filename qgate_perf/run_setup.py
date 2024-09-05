import datetime


class RunSetup:

    def __init__(self, duration_second = 0, start_delay: int = 0, parameters: dict = {}):
        """ Setup of execution

        :param duration_second:     parameter for duration of atomic execution (it is up to function,
                                    if function will reflect the defined value)
        :param start_delay:         maximal time in seconds for waiting to the all executors,
                                    after this time all executors will continue in run. It is usefull
                                    parameter for executor synchronization, value 0 = without synchronization
        :param parameters:          addition parameters for execution
        """
        self._duration_second = duration_second
        self._bulk_row = 1
        self._bulk_col = 1
        self._start_delay = start_delay
        self._when_start = None

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

    @property
    def is_init(self):
        return self.param("__INIT__", False)

    def param(self, key: str, default=None):
        """Return key parameter"""
        if self._parameters:
            return self._parameters.get(key, default)
        return default

    def __getitem__(self, key):
        """Return key parameter, with default value None"""
        return self.param(key, None)

    def __str__(self):
        """Return all keys and values from parameter"""
        out="DUMP>> "
        if self._parameters:
            for key in self._parameters.keys():
                out+=f"{key}: {self._parameters[key]}, "
        return out[:-2]

    @property
    def duration_second(self):
        return self._duration_second

    def set_start_time(self):
        """Define unique start time for all executors. The time has to be setup before executor start."""
        self._when_start = datetime.datetime.now() + datetime.timedelta(seconds=self._start_delay)

    def set_bulk(self, bulk_row, bulk_column):
        self._bulk_row = bulk_row if bulk_row > 0 else 1
        self._bulk_col = bulk_column if bulk_column > 0 else 1
