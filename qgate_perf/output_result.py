import multiprocessing
import os.path
from json import dumps
from datetime import datetime
from qgate_perf.file_marker import FileMarker
from qgate_perf.run_setup import RunSetup
from qgate_perf.helper import Helper
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.output_setup import OutputSetup


class PercentileSummary:
    """Summary data from all executors, for one specific percentile"""
    def __init__(self,
                 percentile,
                 count = 0,
                 call_per_sec_raw = 0,
                 call_per_sec = 0,
                 avrg = 0,
                 std = 0,
                 min = 0,
                 max = 0,
                 executors = 0):
        self.percentile = percentile

        self.count = count
        self.call_per_sec_raw = call_per_sec_raw
        self.call_per_sec = call_per_sec
        self.avrg = avrg
        self.std = std
        self.min = min
        self.max = max
        self.executors = executors

class PerfResult:
    """Output from one performance test (summary data from all executors and for all percentiles)"""

    def __init__(self, state, row, col, process, thread, percentile_summaries: dict[PercentileSummary]):

        self.state = state

        self.bundle_row = row
        self.bundle_col = col

        self.executor_process = process
        self.executor_thread = thread

        self._percentile_summaries = percentile_summaries

    @property
    def percentiles(self) -> dict[PercentileSummary]:
        return self._percentile_summaries

    @percentiles.setter
    def percentiles(self, value):
        self._percentile_summaries = value

    def __getitem__(self, key) -> PercentileSummary:
        return self._percentile_summaries[key]

    def __len__(self):
        return len(self._percentile_summaries)

    def __str__(self):
        info = f"bundle ({self.bundle_row}x{self.bundle_col}), executor ({self.executor_process}x{self.executor_thread}) = "
        for percentile in self._percentile_summaries.keys():
            info += f"{self._percentile_summaries[percentile].call_per_sec} [{int(percentile * 100)}ph], "
        return info[:-2]

class PerfResults:
    """Output from all performance tests"""

    def __init__(self):
        self._results = []
        self._state = True

    @property
    def results(self) -> list[PerfResult]:
        return self._results

    @property
    def state(self):
        return self._state

    def add_state(self, state):
        if state == False:
            self._state = False

    def append(self, item):

        if isinstance(item, PerfResult):
            self._results.append(item)
            self.add_state(item.state)

        if isinstance(item, PerfResults):
            for itm in item._results:
                self._results.append(itm)
                self.add_state(itm.state)

    def __getitem__(self, index) -> PerfResult:
        return self._results[index]

    def __str__(self):
        info = ""
        for i in range(len(self._results)):
            info += f"str(self._results[i])\n"
        return info

class Output:

    def __init__(self, label = None, detail_output = True, output_file = None):
        self._label = label
        self._detail_output = detail_output
        self._output_file = output_file
        self._file = None

    def open(self):
        if self._output_file is not None:
            self._file = self._open_output()

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None

    def _create_percentile_list(self, run_setup: RunSetup, return_dict):

        percentile_list = {}

        # pre-calculation
            # iteration cross executors results
        for return_key in return_dict:
            response = return_dict[return_key]
            if response:
                if response.exception is None:
                    # iteration cross all percentiles
                    for result in response.percentile_results:
                        if result.count > 0:
                            # sum of average time for one call
                            if percentile_list.get(result.percentile, None) is None:
                                percentile_list[result.percentile] = PercentileSummary(result.percentile,
                                                                                       result.count,
                                                                                       0,
                                                                                       0,
                                                                                       result.total_duration / result.count,
                                                                                       result.std,
                                                                                       result.min,
                                                                                       result.max,
                                                                                       1)
                            else:
                                itm = percentile_list[result.percentile]
                                itm.count += result.count
                                itm.avrg += result.total_duration / result.count
                                itm.std += result.std
                                itm.min = min(result.min, itm.min)
                                itm.max = max(result.max, itm.max)
                                itm.executors += 1
                        else:
                            if percentile_list.get(result.percentile, None) is None:
                                percentile_list[result.percentile] = PercentileSummary(result.percentile,
                                                                                       0,
                                                                                       0,
                                                                                       0,
                                                                                       0,
                                                                                       0,
                                                                                       ParallelProbe.MIN_DURATION,
                                                                                       0,
                                                                                       0)

        # define percentile, if not exist
            # if 100 percentile does not exist, create it
        if percentile_list.get(1, None) is None:
            percentile_list[1] = PercentileSummary(1,0,0, 0, 0,0, 0, 0,0)

            # if expected percentile does not exist, create it
        if run_setup.exist("percentile"):
            if percentile_list.get(run_setup["percentile"], None) is None:
                percentile_list[run_setup["percentile"]] = PercentileSummary(run_setup["percentile"], 0, 0, 0, 0, 0, 0, 0, 0)

        # final calculation
        for percentile in percentile_list.values():
            if percentile.executors > 0:
                # Calc clarification (for better understanding):
                #   avrg / count     = average time for one executor (average is cross all calls and executors)
                #   1 / (avrg/count) = average amount of calls per one second (cross executors)
                percentile.call_per_sec_raw  = 0 if (percentile.avrg / percentile.executors) == 0 else (1 / (percentile.avrg / percentile.executors)) * percentile.executors
                percentile.call_per_sec = percentile.call_per_sec_raw * run_setup._bulk_row

                percentile.avrg = 0 if percentile.executors == 0 else percentile.avrg / percentile.executors
                percentile.std = 0 if percentile.executors == 0 else percentile.std / percentile.executors
            else:
                percentile.min = 0
                percentile.max = 0

        return percentile_list

    def _open_output(self):
        dirname = os.path.dirname(self._output_file)
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname, mode=0o777)
        return open(self._output_file, 'a')

    def print(self, out: str, readable_out: str = None):

        # print to the file 'out'
        if self._file is not None:
            self._file.write(out + "\n")

        # print to the console 'readable_out' or 'out'
        print(readable_out if readable_out else out)

    def print_header(self, run_setup: RunSetup=None):
        self._start_tasks = datetime.utcnow()
        self.print(f"############### {self._start_tasks.isoformat(' ')} ###############")
        total, free = Helper.get_memory()
        out = {}
        out[FileMarker.PRF_TYPE] = FileMarker.PRF_HDR_TYPE
        out[FileMarker.PRF_HDR_LABEL] = self._label if self._label is not None else "Noname"
        out[FileMarker.PRF_HDR_BULK] = [run_setup._bulk_row, run_setup._bulk_col]
        out[FileMarker.PRF_HDR_DURATION] = run_setup._duration_second
        if run_setup.exist('percentile'):
            out[FileMarker.PRF_HDR_PERCENTILE] = run_setup['percentile']
        out[FileMarker.PRF_HDR_AVIALABLE_CPU] = multiprocessing.cpu_count()
        out[FileMarker.PRF_HDR_MEMORY] = total
        out[FileMarker.PRF_HDR_MEMORY_FREE] = free
        out[FileMarker.PRF_HDR_HOST] = Helper.get_host()
        out[FileMarker.PRF_HDR_NOW] =  self._start_tasks.isoformat(' ')

        readable_out = {}
        readable_out[FileMarker.HR_PRF_HDR_LABEL] = self._label if self._label is not None else "Noname"
        readable_out[FileMarker.PRF_HDR_BULK] = [run_setup._bulk_row, run_setup._bulk_col]
        readable_out[FileMarker.PRF_HDR_DURATION] = run_setup._duration_second
        if run_setup.exist('percentile'):
            readable_out[FileMarker.HR_PRF_HDR_PERCENTILE] = run_setup['percentile']
        readable_out[FileMarker.PRF_HDR_AVIALABLE_CPU] = multiprocessing.cpu_count()
        readable_out[FileMarker.HR_PRF_HDR_MEMORY] = f"{total}/{free}"

        self.print(dumps(out, separators=OutputSetup().json_separator),
                    dumps(readable_out, separators = OutputSetup().human_json_separator))

    def print_footer(self, final_state):
        seconds = round((datetime.utcnow() - self._start_tasks).total_seconds(), 1)
        self.print(f"############### State: {'OK' if final_state else 'Error'}, "
                    f" Duration: {Helper.get_readable_duration(seconds)} ({seconds}"
                    f" seconds) ###############")

    def print_detail(self, run_setup: RunSetup, return_dict, processes, threads, group=''):
        """
        Print detail from executors

        :param file:            Output stream for print
        :param run_setup:       Setting for executors
        :param return_dict:     Return values from executors
        :param processes:       Number of processes
        :param threads:         Number of threads
        :param group:           Name of group
        :return:                Performance, total calls per one second
        """
        if self._detail_output == True:
            for return_key in return_dict:
                parallel_ret = return_dict[return_key]
                self.print(f"    {str(parallel_ret) if parallel_ret else ParallelProbe.dump_error('SYSTEM overloaded')}",
                           f"    {parallel_ret.readable_str() if parallel_ret else ParallelProbe.readable_dump_error('SYSTEM overloaded')}")

        # new calculation
        percentile_list = self._create_percentile_list(run_setup, return_dict)

        # A2A form
        out = {}
        out[FileMarker.PRF_TYPE] =  FileMarker.PRF_CORE_TYPE
        out[FileMarker.PRF_CORE_PLAN_EXECUTOR_ALL] = processes * threads
        out[FileMarker.PRF_CORE_PLAN_EXECUTOR] = [processes, threads]
        out[FileMarker.PRF_CORE_REAL_EXECUTOR] = percentile_list[1].executors #executors
        out[FileMarker.PRF_CORE_GROUP] = group
        for result in percentile_list.values():
            suffix = f"_{int(result.percentile * 100)}" if result.percentile < 1 else ""
            out[FileMarker.PRF_CORE_TOTAL_CALL + suffix] = result.count                         # ok
            out[FileMarker.PRF_CORE_TOTAL_CALL_PER_SEC_RAW + suffix] = result.call_per_sec_raw  # ok
            out[FileMarker.PRF_CORE_TOTAL_CALL_PER_SEC + suffix] = result.call_per_sec          # ok
            out[FileMarker.PRF_CORE_AVRG_TIME + suffix] = result.avrg                           # ok
            out[FileMarker.PRF_CORE_STD_DEVIATION + suffix] = result.std                        # ok
            out[FileMarker.PRF_CORE_MIN + suffix] = result.min                                  # ok
            out[FileMarker.PRF_CORE_MAX + suffix] = result.max                                  # ok
        out[FileMarker.PRF_CORE_TIME_END] = datetime.utcnow().isoformat(' ')

        # human readable form
        readable_out = {}
        readable_out[FileMarker.HM_PRF_CORE_PLAN_EXECUTOR_ALL] = f"{processes * threads} [{processes},{threads}]"
        readable_out[FileMarker.HM_PRF_CORE_REAL_EXECUTOR] = percentile_list[1].executors # executors
        readable_out[FileMarker.HM_PRF_CORE_GROUP] = group
        for result in percentile_list.values():
            suffix = f"_{int(result.percentile * 100)}" if result.percentile < 1 else ""
            #readable_out[FileMarker.HM_PRF_CORE_TOTAL_CALL + suffix] = result.count
            readable_out[FileMarker.HM_PRF_CORE_TOTAL_CALL + suffix] = result.count
            if result.call_per_sec_raw == result.call_per_sec:
                call_readable = f"{round(result.call_per_sec_raw, OutputSetup().human_precision)}"
            else:
                call_readable = f"{round(result.call_per_sec_raw, OutputSetup().human_precision)}/{round(result.call_per_sec, OutputSetup().human_precision)}"
            readable_out[FileMarker.HM_PRF_CORE_TOTAL_CALL_PER_SEC + suffix] = call_readable
            readable_out[FileMarker.HM_PRF_CORE_AVRG_TIME + suffix] =  round(result.avrg, OutputSetup().human_precision)
            readable_out[FileMarker.HM_PRF_CORE_STD_DEVIATION + suffix] = round(result.std, OutputSetup().human_precision)
            readable_out[FileMarker.PRF_CORE_MIN + suffix] = round(result.min, OutputSetup().human_precision)
            readable_out[FileMarker.PRF_CORE_MAX + suffix] = round(result.max, OutputSetup().human_precision)

        # final dump
        self.print(f"  {dumps(out, separators = OutputSetup().json_separator)}",
                    f"  {dumps(readable_out, separators = OutputSetup().human_json_separator)}")

        return percentile_list
