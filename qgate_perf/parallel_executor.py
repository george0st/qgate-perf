import concurrent.futures
import multiprocessing
import os.path
import json
import gc
from datetime import datetime
from time import sleep
from qgate_perf.file_format import FileFormat
from qgate_perf.run_setup import RunSetup
from qgate_perf.bundle_helper import BundleHelper
from qgate_perf.executor_helper import ExecutorHelper, GraphScope
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_return import RunReturn
from platform import python_version
from packaging import version
from contextlib import suppress
from qgate_perf.output_setup import OutputSetup
from qgate_perf.output_performance import OutputPerformance


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

    def _print(self, file, out: str, readable_out: str = None):

        # print to the file 'out'
        if file is not None:
            file.write(out + "\n")

        # print to the console 'readable_out' or 'out'
        print(readable_out if readable_out else out)

    def _print_header(self, file, run_setup: RunSetup=None):
        self._start_tasks = datetime.utcnow()
        self._print(file, f"############### {self._start_tasks.isoformat(' ')} ###############")
        total, free = self._memory()
        out = {
            FileFormat.PRF_TYPE: FileFormat.PRF_HDR_TYPE,
            FileFormat.PRF_HDR_LABEL: self._label if self._label is not None else "Noname",
            FileFormat.PRF_HDR_BULK: [run_setup._bulk_row, run_setup._bulk_col],
            FileFormat.PRF_HDR_DURATION: run_setup._duration_second,
            FileFormat.PRF_HDR_AVIALABLE_CPU: multiprocessing.cpu_count(),
            FileFormat.PRF_HDR_MEMORY: total,
            FileFormat.PRF_HDR_MEMORY_FREE: free,
            FileFormat.PRF_HDR_HOST: self._host(),
            FileFormat.PRF_HDR_NOW: self._start_tasks.isoformat(' ')
        }
        readable_out = {
            FileFormat.HR_PRF_HDR_LABEL: self._label if self._label is not None else "Noname",
            FileFormat.PRF_HDR_BULK: [run_setup._bulk_row, run_setup._bulk_col],
            FileFormat.PRF_HDR_DURATION: run_setup._duration_second,
            FileFormat.PRF_HDR_AVIALABLE_CPU: multiprocessing.cpu_count(),
            FileFormat.HR_PRF_HDR_MEMORY: f"{total}/{free}"
        }

        self._print(file, json.dumps(out), json.dumps(readable_out, separators = OutputSetup().human_json_separator))

    def _memory(self):

        mem_total, mem_free = "", ""
        with suppress(Exception):
            import psutil

            values=psutil.virtual_memory()
            mem_total=f"{round(values.total/(1073741824),1)} GB"
            mem_free=f"{round(values.free/(1073741824),1)} GB"
        return mem_total, mem_free

    def _host(self):
        """ Return information about the host in format (host_name/ip addr)"""

        host = ""
        with suppress(Exception):
            import socket

            host_name=socket.gethostname()
            ip=socket.gethostbyname(host_name)
            host=f"{host_name}/{ip}"
        return host

    def _print_footer(self, file, final_state):
        seconds = round((datetime.utcnow() - self._start_tasks).total_seconds(), 1)
        self._print(file,
                    f"############### State: {'OK' if final_state else 'Error'}, "
                    f" Duration: {self._readable_duration(seconds)} ({seconds}"
                    f" seconds) ###############")

    def _readable_duration(self, duration_seconds):
        """Return duration in human-readable form"""

        if duration_seconds < 0:
            return "n/a"

        str_duration = []
        days = int(duration_seconds // 86400)
        if days > 0:
            str_duration.append(f"{days} day")
        hours = int(duration_seconds // 3600 % 24)
        if hours > 0:
            str_duration.append(f"{hours} hour")
        minutes = int(duration_seconds // 60 % 60)
        if minutes > 0:
            str_duration.append(f"{minutes} min")
        seconds = int(duration_seconds % 60)
        if seconds > 0:
            str_duration.append(f"{seconds} sec")
        return ' '.join(str_duration)

    def _final_state(self, return_dict):
        """
        Check, if the processing was fine based on check exception in each executor

        :param return_dict:     Outputs from executors
        :return:                True - all is fine, Fals - some exception
        """
        for return_key in return_dict:
            parallel_ret = return_dict[return_key]
            if parallel_ret is None:
                return False
            elif parallel_ret.exception is not None:
                return False
        return True

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
        sum_avrg_time = 0
        sum_deviation = 0
        sum_call = 0
        executors = 0
        total_call_per_sec=0

        for return_key in return_dict:
            parallel_ret = return_dict[return_key]
            if parallel_ret:
                if (parallel_ret.counter > 0):
                    # sum of average time for one call
                    sum_avrg_time = sum_avrg_time + (parallel_ret.total_duration / parallel_ret.counter)
                    sum_deviation += parallel_ret.standard_deviation
                    sum_call += parallel_ret.counter
                    executors += 1
            if (self._detail_output == True):
                self._print(file,
                            f"    {str(parallel_ret) if parallel_ret else ParallelProbe.dump_error('SYSTEM overloaded')}",
                            f"    {parallel_ret.readable_str() if parallel_ret else ParallelProbe.readable_dump_error('SYSTEM overloaded')}")

        if (executors > 0):
            # Calc clarification:
            #   sum_avrg_time / count = average time for one executor (average is cross all calls and executors)
            #   1 / (sum_avrg_time/count) = average amount of calls per one second (cross executors)
            total_call_per_sec = 0 if (sum_avrg_time / executors) == 0 else (1 / (sum_avrg_time / executors)) * executors * run_setup._bulk_row

        out = {
            FileFormat.PRF_TYPE: FileFormat.PRF_CORE_TYPE,
            FileFormat.PRF_CORE_PLAN_EXECUTOR_ALL: processes * threads,
            FileFormat.PRF_CORE_PLAN_EXECUTOR: [processes, threads],
            FileFormat.PRF_CORE_REAL_EXECUTOR: executors,
            FileFormat.PRF_CORE_GROUP: group,
            FileFormat.PRF_CORE_TOTAL_CALL: sum_call,                                                   # ok
            FileFormat.PRF_CORE_TOTAL_CALL_PER_SEC: total_call_per_sec,                                 # ok
            FileFormat.PRF_CORE_AVRG_TIME: 0 if executors == 0 else sum_avrg_time / executors,          # ok
            FileFormat.PRF_CORE_STD_DEVIATION: 0 if executors == 0 else sum_deviation / executors,      # ok
            FileFormat.PRF_CORE_TIME_END: datetime.utcnow().isoformat(' ')
        }
        readable_out = {
            FileFormat.HM_PRF_CORE_PLAN_EXECUTOR_ALL: f"{processes * threads} [{processes},{threads}]",
            FileFormat.HM_PRF_CORE_REAL_EXECUTOR: executors,
            FileFormat.HM_PRF_CORE_GROUP: group,
            FileFormat.HM_PRF_CORE_TOTAL_CALL: sum_call,
            FileFormat.HM_PRF_CORE_TOTAL_CALL_PER_SEC: round(total_call_per_sec, OutputSetup().human_precision),
            FileFormat.HM_PRF_CORE_AVRG_TIME: 0 if executors == 0 else round(sum_avrg_time / executors, OutputSetup().human_precision),
            FileFormat.HM_PRF_CORE_STD_DEVIATION: 0 if executors == 0 else round (sum_deviation / executors, OutputSetup().human_precision)
        }
        self._print(file,
                    f"  {json.dumps(out)}",
                    f"  {json.dumps(readable_out, separators = OutputSetup().human_json_separator)}")

        return total_call_per_sec

    def _open_output(self):
        dirname = os.path.dirname(self._output_file)
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname, mode=0o777)
        return open(self._output_file, 'a')

    def _executeCore(self, run_setup: RunSetup, return_dict, processes=2, threads=2):

        #from qgate_perf.run_return import RunReturn

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

    def run_bulk_executor(self,
                          bulk_list = BundleHelper.ROW_1_COL_10_100,
                          executor_list = ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                          run_setup: RunSetup = None,
                          sleep_between_bulks = 0,
                          return_performance = False):
        """ Run cycle of bulks in cycle of sequences for function execution

        :param bulk_list:           list of bulks for execution in format [[rows, columns], ...]
        :param executor_list:       list of executors for execution in format [[processes, threads, 'label'], ...]
        :param run_setup:           setup of execution
        :param sleep_between_bulks: sleep between bulks
        :param return_performance:  add to the return also performance, return will be state and performance (default is False)
        :return:                    return state, True - all executions was without exceptions,
                                    False - some exceptions
        """
        final_state = True
        count = 0
        performance = []
        for bulk in bulk_list:

            # sleep before other bulk
            count += 1
            if count>1:
                sleep(sleep_between_bulks)

            # execute
            run_setup.set_bulk(bulk[0], bulk[1])

            if return_performance:
                state, bulk_performance = self.run_executor(executor_list, run_setup, return_performance)
                if not state:
                    final_state=False
                for bulk_perf in bulk_performance:
                    performance.append(bulk_perf)
            else:
                if not self.run_executor(executor_list, run_setup):
                    final_state=False
            # memory clean
            gc.collect()

        if return_performance:
            return final_state, performance
        return final_state

    def run_executor(self, executor_list = ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                     run_setup: RunSetup = None,
                     return_performance = False):
        """ Run executor sequences

        :param executor_list:       list of executors for execution in format [[processes, threads, 'label'], ...]
        :param run_setup:           setup of execution
        :param return_performance:  add to the return also performance, return will be state and performance (default is False)
        :return:                    return state, True - all executions was without exceptions,
                                    False - some exceptions
        """
        file = None
        final_state = True
        performance = []
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
                    cals_sec = self._print_detail(file,
                                       run_setup,
                                       return_dict,
                                       executors[0],
                                       executors[1],
                                       '' if len(executors) <= 2 else executors[2])
                    if return_performance:
                        performance.append(OutputPerformance(run_setup.bulk_row,
                                                      run_setup.bulk_col,
                                                      executors[0],
                                                      executors[1],
                                                      cals_sec))
                    if not self._final_state(return_dict):
                        final_state=False

                # memory clean
                gc.collect(generation = 1)

            self._print_footer(file, final_state)

        except Exception as ex:
            self._print(file,f"SYSTEM ERROR in 'run_executor': {type(ex).__name__} - '{str(ex) if ex is not None else '!! Noname exception !!'}'")
            final_state = False
        finally:
            if file is not None:
                file.close()

        if return_performance:
            return final_state, performance
        return final_state

    def run(self, processes = 2, threads = 2, run_setup: RunSetup = None, return_performance = False):
        """ Run execution of parallel call

        :param processes:       how much processes will be used
        :param threads:         how much threads will be used
        :param run_setup:       setup of execution
        :param return_performance:  add to the return also performance, return will be state and performance (default is False)
        :return:                return state, True - all executions was without exceptions,
                                False - some exceptions
        """
        file = None
        final_state=True
        performance = []
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
                cals_sec = self._print_detail(file, run_setup, return_dict, processes, threads)
                if return_performance:
                    performance.append(OutputPerformance(run_setup.bulk_row,
                                                         run_setup.bulk_col,
                                                         processes,
                                                         threads,
                                                         cals_sec))
                if not self._final_state(return_dict):
                    final_state = False

            self._print_footer(file, final_state)

        except Exception as e:
            self._print(file, f"SYSTEM ERROR in 'run': '{str(e) if e is not None else '!! Noname exception !!'}'")
            final_state = False
        finally:
            if file is not None:
                file.close()

        if return_performance:
            return final_state, performance
        return final_state

    def one_run(self, run_setup: RunSetup = None, return_performance = False):
        """ Run test, only one call, execution in new process, with standard write outputs

        :param run_setup:       setting for run
        :param parameters:      parameters for execution, application in case the run_setup is None
        :param return_performance:  add to the return also performance, return will be state and performance (default is False)
        :return:                return state, True - all executions was without exceptions,
                                False - some exceptions
        """

        # setup minimalistic values
        if not run_setup:
            run_setup = RunSetup(duration_second = 0, start_delay = 0)
            run_setup.set_bulk(1,1)

        # run
        if return_performance:
            state, perf = self.run(processes = 1,
                            threads = 1,
                            run_setup = run_setup,
                            return_performance = return_performance)
            return state, perf
        return self.run(processes = 1,
                 threads = 1,
                 run_setup = run_setup)

    def init_run(self, run_setup: RunSetup=None, print_output=False) -> bool:
        """ Init call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file). One new parameter was added '__INIT__': True

        :param parameters:      parameters for execution, application in case the run_setup is None
        :return:                return state, True - execution was without exception,
                                False - an exception
        """

        if run_setup:
            test_parameters = run_setup._parameters.copy() if run_setup._parameters else {}
        else:
            test_parameters={}
        test_parameters["__INIT__"] = True
        test_run_setup=RunSetup(duration_second=0, start_delay=0,parameters=test_parameters)
        if run_setup:
            test_run_setup.set_bulk(run_setup.bulk_row, run_setup.bulk_col)
        else:
            test_run_setup.set_bulk(1, 1)
        return self.test_run(test_run_setup, print_output)

    def test_run(self, run_setup: RunSetup=None, print_output=False) -> bool:
        """ Test call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file)

        :param run_setup:       setting for run
        :param parameters:      parameters for execution, application in case the run_setup is None
        :return:                return state, True - execution was without exception,
                                False - an exception
        """

        # init
        key="test-no-parallel"
        dictionary = {key: ""}
        run_return = RunReturn(key, dictionary)

        if not run_setup:
            run_setup = RunSetup(duration_second=0, start_delay=0)
        run_setup.set_start_time()

        # test call
        self._func_wrapper(self._func, run_return, run_setup)

        # return output
        ret=dictionary[key]
        if ret:
            if print_output:
                print(str(ret))
            if ret.exception is not None:
                return False
        return True

    @staticmethod
    def create_graph_static(input_file, output_graph_dir = "output", scope: GraphScope = GraphScope.all, picture_dpi = 100, suppress_error = False) -> list[str]:
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

        if GraphScope.perf in scope:
            from qgate_graph.graph_performance import GraphPerformance

            graph = GraphPerformance(picture_dpi)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-perf"), suppress_error):
                output_file.append(file)

        if GraphScope.exe in scope:
            from qgate_graph.graph_executor import GraphExecutor

            graph = GraphExecutor(picture_dpi)
            for file in graph.generate_from_file(input_file, os.path.join(output_graph_dir,"graph-exec"), suppress_error):
                output_file.append(file)

        return output_file

    def create_graph(self, output_graph_dir = "output", scope: GraphScope = GraphScope.all, picture_dpi = 100, suppress_error = False) -> list[str]:
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
