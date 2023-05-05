import datetime
import time
import os, sys, numpy as np
import json
from qgate_perf.file_format import FileFormat
from qgate_perf.run_setup import RunSetup

class ParallelReturn:
    """ Provider of return from executor """

    def __init__(self, run_setup: RunSetup, exception=None):
        """
        Init for parallel run & procedure for executor synchronization

        :param run_setup:      Information about executor start
        :param exception:       In case of error
        """
        self.counter = 0
        self.total_duration = 0
        self.min_duration = sys.maxsize
        self.max_duration = 0
        self.durations = []
        self.standard_deviation=0
        self.pid = os.getpid()
        self.exception = exception

        self.track_time={}
        self.track_time[FileFormat.PRF_DETAIL_TIME_INIT] = datetime.datetime.utcnow()

        if run_setup:
            # init incremental calculation of standard deviation
            self.stddev = self.StandardDeviation(ddof=0)

            # wait for other executors
            self._wait_for_others(run_setup.when_start)

            # key part of init timer (import for stop parallel run)
            self.init_time = time.time()
            self.track_time[FileFormat.PRF_DETAIL_TIME_START] = datetime.datetime.utcnow()
            self.duration_second = run_setup.duration_second

    def add_timetrack_only_label(self, label):
        self.track_time.append(label)

    def add_time_track(self, label):
        self.track_time.append(f"{label}: {datetime.datetime.now()}")

    def start(self):
        """ Start measurement each test"""
        self.start_time_one_shot = time.time()

    def stop(self):
        """ Test, if it is possible to stop execution

        :return:   True - stop execution, False - continue in execution
        """
        self.stop_time_one_shot = time.time()
        duration_one_shot = self.stop_time_one_shot - self.start_time_one_shot

        self.counter += 1
        self.total_duration += duration_one_shot

        # calc standard deviation incrementally
        self.stddev.include(duration_one_shot)

        # setup new min
        if duration_one_shot<self.min_duration:
            self.min_duration=duration_one_shot

        # setup new max
        if duration_one_shot>self.max_duration:
            self.max_duration=duration_one_shot

        # Is it possible to end performance testing?
        if ((self.stop_time_one_shot - self.init_time) >= self.duration_second):
            # write time
            self.track_time[FileFormat.PRF_DETAIL_TIME_END]=datetime.datetime.utcnow()
            # calc standard deviation
            self.standard_deviation=self.stddev.std
            return True
        return False

    def _wait_for_others(self, when_start, tollerance=0.1):
        """ Waiting for other executors

            :param when_start:      datetime, when to start execution
            :param tollerance:      time tollerance in second (when it does not make to wait), default is 100 ms
        """
        # wait till specific time (the time for run is variable for each exector based on system processing and delay)
        sleep_time = when_start - datetime.datetime.now()
        sleep_time = sleep_time.total_seconds()

        # define size of tollerance for synchronization
        if (sleep_time > tollerance):
            time.sleep(sleep_time)

    def ToString(self):
        """ Provider view to return value """
        if self.exception is None:
            out={
                FileFormat.PRF_TYPE: FileFormat.PRF_DETAIL_TYPE,
                FileFormat.PRF_DETAIL_PROCESSID: self.pid,
                FileFormat.PRF_DETAIL_CALLS: self.counter,
                FileFormat.PRF_DETAIL_TOTAL: self.total_duration,
                FileFormat.PRF_DETAIL_AVRG: self.total_duration / self.counter,
                FileFormat.PRF_DETAIL_MIN: self.min_duration,
                FileFormat.PRF_DETAIL_MAX: self.max_duration,
                FileFormat.PRF_DETAIL_STDEV: self.standard_deviation,
                FileFormat.PRF_DETAIL_TIME_INIT: self.track_time[FileFormat.PRF_DETAIL_TIME_INIT].isoformat(' '),
                FileFormat.PRF_DETAIL_TIME_START: self.track_time[FileFormat.PRF_DETAIL_TIME_START].isoformat(' '),
                FileFormat.PRF_DETAIL_TIME_END: self.track_time[FileFormat.PRF_DETAIL_TIME_END].isoformat(' ')
            }
            return json.dumps(out)
        else:
            out={
                FileFormat.PRF_TYPE: FileFormat.PRF_DETAIL_TYPE,
                FileFormat.PRF_DETAIL_PROCESSID: self.pid,
                FileFormat.PRF_DETAIL_CALLS: self.counter,
                FileFormat.PRF_DETAIL_ERR: str(self.exception)
            }
            return json.dumps(out)

    class StandardDeviation:
        """
        Welford's alg for incrementally calculation of standard deviation
        """
        def __init__(self, ddof=1):
            self.ddof, self.n, self.mean, self.M2 = ddof, 0, 0.0, 0.0

        def include(self, data):
            self.n += 1
            self.delta = data - self.mean
            self.mean += self.delta / self.n
            self.M2 += self.delta * (data - self.mean)

        @property
        def variance(self):
            return self.M2 / (self.n - self.ddof)

        @property
        def std(self):
            """ Standard deviation """
            return np.sqrt(self.variance)
