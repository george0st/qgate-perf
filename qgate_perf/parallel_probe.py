import os
import json
from time import time, sleep, perf_counter
from datetime import datetime
from qgate_perf.standard_deviation import StandardDeviation
from qgate_perf.file_format import FileFormat
from qgate_perf.run_setup import RunSetup
from qgate_perf.output_setup import OutputSetup
from math import nan


class ParallelProbe:
    """ Provider probe for parallel test tuning """

    def __init__(self, run_setup: RunSetup, exception=None):
        """
        Init for parallel run & procedure for executor synchronization

        :param run_setup:      Information about executor start
        :param exception:       In case of error
        """
        self.counter = 0
        self.pid = os.getpid()
        self.exception = exception

        if exception is None:
            self.total_duration = 0
            self.min_duration = 1000000000
            self.max_duration = 0
            self.standard_deviation = 0
            self.track_init = datetime.utcnow()
            if run_setup:
                # init incremental calculation of standard deviation
                self.stddev = StandardDeviation(ddof=0)

                # wait for other executors
                ParallelProbe._wait_for_others(run_setup.when_start)

                self.duration_second = run_setup.duration_second

                # key part of init timer (import for stop parallel run)
                self.init_time = time()
                self.track_start = datetime.utcnow()
                self.track_end = datetime(1970, 1, 1)

    def start(self):
        """ Start measurement each test"""
        self.start_time_one_shot = perf_counter()

    def stop(self) -> bool:
        """Test, if it is possible to stop execution, based on duration of test

        :return:   True - stop execution, False - continue in execution
        """
        stop_time_one_shot = perf_counter()

        duration_one_shot = stop_time_one_shot - self.start_time_one_shot
        self._core_calc(duration_one_shot)

        # Is it possible to end performance testing?
        if (time() - self.init_time) >= self.duration_second:
            self._core_close()
            return True
        return False

    def _core_calc(self, duration_one_shot):
        """Core for calculation (and simulation)"""

        self.counter += 1
        self.total_duration += duration_one_shot

        # calc standard deviation incrementally
        self.stddev.include(duration_one_shot)

        # setup new min
        if duration_one_shot < self.min_duration:
            self.min_duration = duration_one_shot

        # setup new max
        if duration_one_shot > self.max_duration:
            self.max_duration = duration_one_shot

    def _core_close(self):
        # write time
        self.track_end = datetime.utcnow()
        # calc standard deviation
        self.standard_deviation = self.stddev.std
        # release unused sources (we calculated standard deviation)
        del self.stddev

    @staticmethod
    def _wait_for_others(when_start, tolerance=0.1):
        """ Waiting for other executors

            :param when_start:      datetime, when to start execution
            :param tolerance:       time tolerance in second (when it does not make to wait), default is 100 ms
        """
        # wait till specific time (the time for run is variable for each executor based on system processing and delay)
        sleep_time = when_start - datetime.now()
        sleep_time = sleep_time.total_seconds()

        # define size of tolerance for synchronization
        if sleep_time > tolerance:
            sleep(sleep_time)

    def __str__(self):
        """ Provider view to return value """

        if self.exception is None:
            return json.dumps({
                FileFormat.PRF_TYPE: FileFormat.PRF_DETAIL_TYPE,
                FileFormat.PRF_DETAIL_PROCESSID: self.pid,                          # info
                FileFormat.PRF_DETAIL_CALLS: self.counter,                          # for perf graph
                FileFormat.PRF_DETAIL_AVRG: nan if self.counter == 0 else self.total_duration / self.counter,
                FileFormat.PRF_DETAIL_MIN: self.min_duration,                       # info
                FileFormat.PRF_DETAIL_MAX: self.max_duration,                       # info
                FileFormat.PRF_DETAIL_STDEV: self.standard_deviation,               # for perf graph
                FileFormat.PRF_DETAIL_TOTAL: self.total_duration,                   # for perf graph
                FileFormat.PRF_DETAIL_TIME_INIT: self.track_init.isoformat(' '),    # for executor graph
                FileFormat.PRF_DETAIL_TIME_START: self.track_start.isoformat(' '),  # for executor graph
                FileFormat.PRF_DETAIL_TIME_END: self.track_end.isoformat(' ')       # for executor graph
            })
        else:
            return ParallelProbe.dump_error(self.exception, self.pid, self.counter)

    def readable_str(self, compact_form = True):
        """Provide view to return value in readable and shorter form (for human check)"""

        if self.exception is None:
            return json.dumps({
                FileFormat.HR_PRF_DETAIL_CALLS: self.counter,
                FileFormat.HR_PRF_DETAIL_AVRG: nan if self.counter == 0 else round(self.total_duration / self.counter, OutputSetup().human_precision),
                FileFormat.PRF_DETAIL_MIN: round(self.min_duration, OutputSetup().human_precision),
                FileFormat.PRF_DETAIL_MAX: round(self.max_duration, OutputSetup().human_precision),
                FileFormat.HR_PRF_DETAIL_STDEV: round(self.standard_deviation, OutputSetup().human_precision),
                FileFormat.HR_PRF_DETAIL_TOTAL: round(self.total_duration, OutputSetup().human_precision)
            }, separators = OutputSetup().human_json_separator if compact_form else (', ', ': '))
        else:
            return ParallelProbe.readable_dump_error(self.exception, self.pid, self.counter)

    @staticmethod
    def dump_error(exception, pid=0, counter=0):
        return json.dumps({
            FileFormat.PRF_TYPE: FileFormat.PRF_DETAIL_TYPE,
            FileFormat.PRF_DETAIL_PROCESSID: pid,
            FileFormat.PRF_DETAIL_CALLS: counter,
            FileFormat.PRF_DETAIL_ERR: str(exception)
        })

    @staticmethod
    def readable_dump_error(exception, pid=0, counter=0):
        return json.dumps({
            FileFormat.PRF_DETAIL_CALLS: counter,
            FileFormat.PRF_DETAIL_ERR: str(exception)
        }, separators = OutputSetup().human_json_separator)
