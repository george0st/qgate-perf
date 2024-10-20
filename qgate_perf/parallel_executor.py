import concurrent.futures
import multiprocessing
import os.path
import gc
from json import dumps
from datetime import datetime
from time import sleep
from qgate_perf.file_marker import FileMarker
from qgate_perf.run_setup import RunSetup
from qgate_perf.helper import ExecutorHelper, GraphScope, BundleHelper, get_host, get_memory, get_readable_duration
from qgate_perf.parallel_probe import ParallelProbe, PercentileSummary
from qgate_perf.run_return import RunReturn
from platform import python_version
from packaging import version
from qgate_perf.output_setup import OutputSetup
from qgate_perf.output_result import PerfResult, PerfResults


def _executor_wrapper(func, run_return: RunReturn, run_setup: RunSetup):
    """
    Lightweight internal wrapper for exception handling in executor

    :param func:        original call function
    :param run_return:  return object
    :param run_setup:   setup for run
    """
    try:
        if not func:
            raise ValueError("Missing function for performance tests, update this code 'ParallelExecutor(null)'.")
        run_return.probe=func(run_setup)
    except Exception as ex:
        run_return.probe=ParallelProbe(None, f"{type(ex).__name__}: {str(ex)}")


class ParallelExecutor:
    """ Helper for parallel execution of defined function (via start new process with aim to avoid GIL) """

    def __init__(self,
                 func,
                 label = None,
                 detail_output = True,
                 output_file = None,
                 init_each_bulk = False):
        """ Setting of execution

        :param func:            function for parallel run in format see 'def my_func(run_setup: RunSetup) -> ParallelProbe:'
        :param label:           text label for parallel run
        :param detail_output:   provide detailed output from visualization of time, when executor was started
                                see usage in method create_graph_exec, default is True
        :param output_file:     output to the file, default is without file
        :param init_each_bulk:  call 'init_run' before each bulk (useful e.g. change amount of columns in target),
                                default is False
        """
        self._func = func
        self._func_wrapper = _executor_wrapper
        self._detail_output = detail_output
        self._label = label
        self._output_file = output_file
        self._init_each_bulk = init_each_bulk

        # Technical point, how to close Process
        #   in python >= 3.7 Close() as soft closing
        #   in python < 3.7 Terminate() as hard closing (the Close method does not exist in python lower versions)
        self._process_close=True if version.parse(python_version()) >= version.parse("3.7") else False

    # region CORE

    def _coreThreadClassPool(self, threads, return_key, return_dict, run_setup: RunSetup):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                features = []
                for threadKey in range(threads):
                    run_return=RunReturn(f"{return_key}x{threadKey}", return_dict)
                    features.append(
                        executor.submit(self._func_wrapper, self._func, run_return, run_setup))

                for future in concurrent.futures.as_completed(features):
                    future.result()
        except Exception as ex:
            print(f"SYSTEM ERROR in '_coreThreadClassPool': {type(ex).__name__} - '{str(ex)}'")

    def _executeCore(self, run_setup: RunSetup, return_dict, processes=2, threads=2):

        proc = []
        # define synch time for run of all executors
        run_setup.set_start_time()

        try:
            if threads == 1:
                for process_key in range(processes):
                    run_return = RunReturn(process_key, return_dict)
                    p = multiprocessing.Process(target=self._func_wrapper,
                                args=(self._func, run_return, run_setup))
                    proc.append(p)
            else:
                for process_key in range(processes):
                    p = multiprocessing.Process(target=self._coreThreadClassPool,
                                args=(threads, process_key, return_dict, run_setup))
                    proc.append(p)

            # start
            for p in proc:
                p.start()

            # wait for finish
            for p in proc:
                p.join()
                if self._process_close:
                    p.close()       # soft close
                else:
                    p.terminate()   # hard close
        except Exception as ex:
            print(f"SYSTEM ERROR in '_executeCore': '{str(ex)}'")

    # endregion CORE

    # region PRINT OUTPUT
    def _open_output(self):
        dirname = os.path.dirname(self._output_file)
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname, mode=0o777)
        return open(self._output_file, 'a')

    def _print(self, file, out: str, readable_out: str = None):

        # print to the file 'out'
        if file is not None:
            file.write(out + "\n")

        # print to the console 'readable_out' or 'out'
        print(readable_out if readable_out else out)

    def _print_header(self, file, run_setup: RunSetup=None):
        self._start_tasks = datetime.utcnow()
        self._print(file, f"############### {self._start_tasks.isoformat(' ')} ###############")
        total, free = get_memory()
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
        out[FileMarker.PRF_HDR_HOST] = get_host()
        out[FileMarker.PRF_HDR_NOW] =  self._start_tasks.isoformat(' ')

        readable_out = {}
        readable_out[FileMarker.HR_PRF_HDR_LABEL] = self._label if self._label is not None else "Noname"
        readable_out[FileMarker.PRF_HDR_BULK] = [run_setup._bulk_row, run_setup._bulk_col]
        readable_out[FileMarker.PRF_HDR_DURATION] = run_setup._duration_second
        if run_setup.exist('percentile'):
            readable_out[FileMarker.HR_PRF_HDR_PERCENTILE] = run_setup['percentile']
        readable_out[FileMarker.PRF_HDR_AVIALABLE_CPU] = multiprocessing.cpu_count()
        readable_out[FileMarker.HR_PRF_HDR_MEMORY] = f"{total}/{free}"


        self._print(file,
                    dumps(out, separators=OutputSetup().json_separator),
                    dumps(readable_out, separators = OutputSetup().human_json_separator))

    def _print_footer(self, file, final_state):
        seconds = round((datetime.utcnow() - self._start_tasks).total_seconds(), 1)
        self._print(file,
                    f"############### State: {'OK' if final_state else 'Error'}, "
                    f" Duration: {get_readable_duration(seconds)} ({seconds}"
                    f" seconds) ###############")

    def _print_detail(self, file, run_setup: RunSetup, return_dict, processes, threads, group=''):
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
                self._print(file,
                            f"    {str(parallel_ret) if parallel_ret else ParallelProbe.dump_error('SYSTEM overloaded')}",
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
        self._print(file,
                    f"  {dumps(out, separators = OutputSetup().json_separator)}",
                    f"  {dumps(readable_out, separators = OutputSetup().human_json_separator)}")

        return percentile_list

    # endregion PRINT OUTPUT

    def _check_state(self, return_dict):
        """
        Check, if the processing was fine based on check exception in each executor

        :param return_dict:     Outputs from executors
        :return:                True - all is fine, False - some exception
        """
        for return_key in return_dict:
            parallel_ret = return_dict[return_key]
            if parallel_ret is None:
                return False
            elif parallel_ret.exception is not None:
                return False
        return True

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


    # region RUN's

    def run_bulk_executor(self,
                          bulk_list = BundleHelper.ROW_1_COL_10_100,
                          executor_list = ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                          run_setup: RunSetup = None,
                          sleep_between_bulks = 0,
                          performance_detail = False) -> PerfResults:
        """ Run cycle of bulks in cycle of sequences for function execution

        :param bulk_list:           list of bulks for execution in format [[rows, columns], ...]
        :param executor_list:       list of executors for execution in format [[processes, threads, 'label'], ...]
        :param run_setup:           setup of execution
        :param sleep_between_bulks: sleep between bulks
        :param performance_detail:  add to the return also performance details (default is False)
        :return:                    return performance results with key information about the 'state'. The state
                                    True - all executions was without exceptions, False - some exceptions.
        """
        performance = PerfResults()
        count = 0

        for bulk in bulk_list:

            # sleep before other bulk
            count += 1
            if count>1:
                sleep(sleep_between_bulks)

            # execute
            run_setup.set_bulk(bulk[0], bulk[1])
            bulk_performance = self.run_executor(executor_list, run_setup, performance_detail)
            if performance_detail:
                performance.append(bulk_performance)
            else:
                performance.add_state(bulk_performance.state)

            # memory clean
            gc.collect()

        return performance

    def run_executor(self, executor_list = ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                     run_setup: RunSetup = None,
                     performance_detail = False) -> PerfResults:
        """ Run executor sequences

        :param executor_list:       list of executors for execution in format [[processes, threads, 'label'], ...]
        :param run_setup:           setup of execution
        :param performance_detail:  add to the return also performance details (default is False)
        :return:                    return performance results with key information about the 'state'. The state
                                    True - all executions was without exceptions, False - some exceptions.
        """
        performance = PerfResults()
        file = None

        print('Execution...')

        try:
            if self._init_each_bulk:
                self.init_run(run_setup)

            if self._output_file is not None:
                file=self._open_output()

            self._print_header(file, run_setup)

            for executors in executor_list:
                # execution
                with multiprocessing.Manager() as manager:
                    return_dict = manager.dict()
                    self._executeCore(run_setup, return_dict, executors[0], executors[1])
                    percentile_list = self._print_detail(file,
                                       run_setup,
                                       return_dict,
                                       executors[0],
                                       executors[1],
                                       '' if len(executors) <= 2 else executors[2])

                    # check state
                    state = self._check_state(return_dict)
                    if performance_detail:
                        performance.append(PerfResult(state,
                                                      run_setup.bulk_row,
                                                      run_setup.bulk_col,
                                                      executors[0],
                                                      executors[1],
                                                      percentile_list))
                    else:
                        performance.add_state(state)

                # memory clean
                gc.collect(generation = 1)

            self._print_footer(file, performance.state)

        except Exception as ex:
            self._print(file,f"SYSTEM ERROR in 'run_executor': {type(ex).__name__} - '{str(ex) if ex is not None else '!! Noname exception !!'}'")
            performance.add_state(False)
        finally:
            if file is not None:
                file.close()

        return performance

    def run(self, processes = 2, threads = 2, run_setup: RunSetup = None, performance_detail = False) -> PerfResults:
        """ Run execution of parallel call

        :param processes:       how much processes will be used
        :param threads:         how much threads will be used
        :param run_setup:       setup of execution
        :param performance_detail:  add to the return also performance details (default is False)
        :return:                    return performance results with key information about the 'state'. The state
                                    True - all executions was without exceptions, False - some exceptions.
        """
        performance = PerfResults()
        file = None

        print('Execution...')

        try:
            if self._init_each_bulk:
                self.init_run(run_setup)

            if self._output_file is not None:
                file = self._open_output()

            self._print_header(file, run_setup)

            # Execution
            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                self._executeCore(run_setup, return_dict, processes, threads)
                percentile_list = self._print_detail(file, run_setup, return_dict, processes, threads)

                # check state
                state = self._check_state(return_dict)
                if performance_detail:
                    performance.append(PerfResult(state,
                                                  run_setup.bulk_row,
                                                  run_setup.bulk_col,
                                                  processes,
                                                  threads,
                                                  percentile_list))
                else:
                    performance.add_state(state)

            self._print_footer(file, performance.state)

        except Exception as e:
            self._print(file, f"SYSTEM ERROR in 'run': '{str(e) if e is not None else '!! Noname exception !!'}'")
            performance.add_state(False)
        finally:
            if file is not None:
                file.close()

        return performance

    def one_run(self, run_setup: RunSetup = None, performance_detail = False) -> PerfResults:
        """ Run test, only one call, execution in new process, with standard write outputs

        :param run_setup:       setting for run
        :param performance_detail:  add to the return also performance details (default is False)
        :return:                    return performance results with key information about the 'state'. The state
                                    True - all executions was without exceptions, False - some exceptions.
        """

        # setup minimalistic values
        if not run_setup:
            run_setup = RunSetup(duration_second = 0, start_delay = 0)
            run_setup.set_bulk(1,1)

        # run
        return self.run(processes = 1,
                        threads = 1,
                        run_setup = run_setup,
                        performance_detail = performance_detail)

    def init_run(self, run_setup: RunSetup=None, print_output=False) -> bool:
        """ Init call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file). One new parameter was added '__INIT__': True

        :param run_setup:       setting for run
        :param print_output:    True - with print output, False - without print output
        :return:                return state, True - execution was without exception,
                                False - an exception
        """

        if run_setup:
            test_parameters = run_setup._parameters.copy() if run_setup._parameters else {}
        else:
            test_parameters = {}
        test_parameters["__INIT__"] = True
        test_run_setup=RunSetup(duration_second = 0, start_delay = 0, parameters = test_parameters)
        if run_setup:
            test_run_setup.set_bulk(run_setup.bulk_row, run_setup.bulk_col)
        else:
            test_run_setup.set_bulk(1, 1)
        return self.test_run(test_run_setup, print_output)

    def test_run(self, run_setup: RunSetup=None, print_output=False) -> bool:
        """ Test call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file)

        :param run_setup:       setting for run
        :param print_output:    True - with print output, False - without print output
        :return:                return state, True - execution was without exception,
                                False - an exception
        """

        # init
        key = "test-no-parallel"
        dictionary = {key: ""}
        run_return = RunReturn(key, dictionary)

        if not run_setup:
            run_setup = RunSetup(duration_second=0, start_delay=0)
        run_setup.set_start_time()

        # test call
        self._func_wrapper(self._func, run_return, run_setup)

        # return output
        ret = dictionary[key]
        if ret:
            if print_output:
                print(str(ret))
            if ret.exception is not None:
                return False
        return True

    # endregion RUN

    # region GRAPH's

    @staticmethod
    def create_graph_static(input_file, output_graph_dir = "output", scope: GraphScope = GraphScope.all_no_raw, picture_dpi = 100, suppress_error = False) -> list[str]:
        """
        Generate graph(s) based on output from performance tests

        :param input_file:          source file with detail of outputs from performance tests
        :param output_graph_dir:    directory for graph outputs (with subdirectory 'graph-perf' and 'graph-exec')
        :param scope:               definition of scope generation (default ExecutorGraph.all)
        :param picture_dpi:         quality of picture (default is 100 DPI)
        :param suppress_error:      suppress error (default is False)
        :return:                    list of generated files
        """
        output_file=[]

        #  PERF
        if GraphScope.perf in scope:
            from qgate_graph.graph_performance import GraphPerformance

            # raw format False
            graph = GraphPerformance(picture_dpi, raw_format = False)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-perf"), suppress_error):
                output_file.append(file)

        if GraphScope.perf_raw in scope:
            from qgate_graph.graph_performance import GraphPerformance

            # raw format True
            graph = GraphPerformance(picture_dpi, raw_format = True)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-perf"), suppress_error):
                output_file.append(file)

        # PERF CSV
        if GraphScope.perf_csv in scope:
            from qgate_graph.graph_performance_csv import GraphPerformanceCsv

            # raw format False
            graph = GraphPerformanceCsv(raw_format = False)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-perf"), suppress_error):
                output_file.append(file)

        if GraphScope.perf_csv_raw in scope:
            from qgate_graph.graph_performance_csv import GraphPerformanceCsv

            # raw format True
            graph = GraphPerformanceCsv(raw_format = True)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-perf"), suppress_error):
                output_file.append(file)

        # PERF TXT
        if GraphScope.perf_txt in scope:
            from qgate_graph.graph_performance_txt import GraphPerformanceTxt

            # raw format False
            graph = GraphPerformanceTxt(raw_format=False)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir, "graph-perf"), suppress_error):
                output_file.append(file)

        if GraphScope.perf_txt_raw in scope:
            from qgate_graph.graph_performance_txt import GraphPerformanceTxt

            # raw format True
            graph = GraphPerformanceTxt(raw_format=True)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir, "graph-perf"), suppress_error):
                output_file.append(file)

        # EXE
        if GraphScope.exe in scope:
            from qgate_graph.graph_executor import GraphExecutor

            graph = GraphExecutor(picture_dpi)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-exec"), suppress_error):
                output_file.append(file)

        return output_file

    def create_graph(self, output_graph_dir = "output", scope: GraphScope = GraphScope.all_no_raw, picture_dpi = 100, suppress_error = False) -> list[str]:
        """
        Generate graph(s) based on output from performance tests.
        The outputs will be in subdirectories 'graph-perf' and 'graph-exec'.

        :param output_graph_dir:    directory for graph outputs (with subdirectory 'graph-perf' and 'graph-exec')
        :param scope:               definition of scope generation (default ExecutorGraph.all)
        :param picture_dpi:         quality of picture (default is 100 DPI)
        :param suppress_error:      suppress error (default is False)
        :return:                    list of generated files
        """
        return ParallelExecutor.create_graph_static(self._output_file,
                                      output_graph_dir,
                                      scope,
                                      picture_dpi,
                                      suppress_error)

    def create_graph_perf(self, output_graph_dir = "output", picture_dpi = 100, suppress_error = False) -> list[str]:
        """
        Generate performance graph(s) based on output from performance tests.
        The outputs will be in subdirectory 'graph-perf'.

        :param output_graph_dir:    directory for graph outputs (with subdirectory 'graph-perf')
        :param picture_dpi:         quality of picture (default is 100 DPI)
        :param suppress_error:      suppress error (default is False)
        :return:                    list of generated files
        """
        return ParallelExecutor.create_graph_static(self._output_file,
                                      output_graph_dir,
                                      GraphScope.perf,
                                      picture_dpi,
                                      suppress_error)

    def create_graph_exec(self, output_graph_dir = "output", picture_dpi = 100, suppress_error = False) -> list[str]:
        """
        Generate executors graph(s) based on output from performance tests.
        The outputs will be in subdirectory 'graph-exec'.

        :param output_graph_dir:    directory for graph outputs (with subdirectory 'graph-exec')
        :param picture_dpi:         quality of picture (default is 100 DPI)
        :param suppress_error:      suppress error (default is False)
        :return:                    list of generated files
        """
        return ParallelExecutor.create_graph_static(self._output_file,
                                      output_graph_dir,
                                      GraphScope.exe,
                                      picture_dpi,
                                      suppress_error)

    # endregion GRAPHS