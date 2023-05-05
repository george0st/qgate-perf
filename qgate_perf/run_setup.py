import datetime

class RunSetup:

    def __init__(self, duration_second, start_delay: int, parameters: dict={}):
        """ Setup of execution

        :param duration_second:     parametrs for duration of atomic execution (it is up to function, if it will reflect the value)
        :param start_delay:         maximal time for waiting/synchronization, before execution of all executors
        :param parameters:          addition parameters for execution
        """
        self.duration_second=duration_second
        self.bulk_row = 1
        self.bulk_col = 10
        self.start_delay=start_delay

        # collection of specific keys for project such as project_name, feature_set_name, etc.
        self.parameters=parameters

    def set_start_time(self):
        self.when_start = datetime.datetime.now() + datetime.timedelta(seconds=self.start_delay)

    def set_output_handler(self, return_key, return_dict):
        self.return_key=return_key
        self.return_dict=return_dict

    def set_output(self, ret = None):
        if self.return_dict is not None:
            self.return_dict[self.return_key] = ret

    def set_bulk(self, bulk_row, bulk_column):
        self.bulk_row = bulk_row if bulk_row > 0 else 1
        self.bulk_col = bulk_column if bulk_column > 0 else 1
