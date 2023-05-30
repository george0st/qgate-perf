import gc
import os.path
from multiprocessing import Process
import multiprocessing
import threading
import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import json
from qgate_perf.file_format import FileFormat
from qgate_perf.run_setup import RunSetup
from qgate_perf.bundle_helper import BundleHelper
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_return import RunReturn

class ParallelExecutor:
    """ Helper for parallel execution of defined function (via start new process with aim to avoid GIL) """

    def __init__(self, func, label=None, detail_output=True, output_file=None):
        """ Setting of execution

        :param func:            function for parallel run
        :param label:           text label for parallel run
        :param detail_output:   provide details output from executors
        :param output_file:     output to the file, defualt is without file
        """
        self._func = func
        self._detail_output = detail_output
        self._label =label
        self._output_file = output_file


    def _coreThreadClassPool(self, threads, return_key, return_dict, run_setup: RunSetup):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            features = []
            for threadKey in range(threads):
                run_return=RunReturn(f"{return_key}x{threadKey}", return_dict)
                features.append(
                    executor.submit(self._func, run_return, run_setup))

            for future in concurrent.futures.as_completed(features):
                future.result()

    def _coreThreadClass(self, threads, return_key, return_dict, run_setup):
        thrd = []
        for threadKey in range(threads):
            t = threading.Thread(target=self._func,
                                 args=(str(return_key) + "x" + str(threadKey), return_dict, run_setup))
            thrd.append(t)

        # start
        for t in thrd:
            t.start()

        # wait for finish
        for t in thrd:
            t.join()
            t = None

    def _coreThread(func, threads, return_key, return_dict, run_setup):
        thrd = []
        for thread_key in range(threads):
            t = threading.Thread(target=func,
                                 args=(str(return_key) + "x" + str(thread_key), return_dict, run_setup))
            thrd.append(t)

        # start
        for t in thrd:
            t.start()

        # wait for finish
        for t in thrd:
            t.join()
            t = None

    def _coreThreadPool(func, threads, return_key, return_dict, run_setup):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            features = []
            for thread_key in range(threads):
                features.append(
                    executor.submit(func, f"{return_key}x{thread_key}", return_dict, run_setup))

            for future in concurrent.futures.as_completed(features):
                future.result()

    def _executeCore(self, run_setup: RunSetup, return_dict, processes=2, threads=2):

        from qgate_perf.run_return import RunReturn

        proc = []

        # define synch time for run of all executors
        run_setup.set_start_time()

        if threads == 1:
            for process_key in range(processes):
                run_return=RunReturn(process_key, return_dict)
                p = Process(target=self._func,
                            args=(run_return, run_setup))
# oldversion                args=(process_key, return_dict, run_setup))

                proc.append(p)
        else:
            for process_key in range(processes):
                p = Process(target=self._coreThreadClassPool,
                            args=(threads, process_key, return_dict, run_setup))
# oldversion    p = Process(target=self._coreThreadClassPool,
                #                p = Process(target=self._coreThreadClassPool,
                # p = Process(target=self._coreThreadClass, args=(threads, process_key, return_dict, run_setup))
                # p = Process(target=ParallelExecutor._coreThread, args=(self.func, threads, process_key, return_dict, run_setup))
                # p = Process(target=ParallelExecutor._coreThreadPool, args=(self.func, threads, process_key, return_dict, run_setup))
                proc.append(p)

        # start
        for p in proc:
            p.start()

        # wait for finish
        for p in proc:
            p.join()
            p.close()

    def _print(self, file, out: str):
        if file is not None:
            file.write(out + "\n")
        print(out)

    def _print_header(self, file, run_setup: RunSetup=None):
        self._start_tasks = datetime.datetime.utcnow()
        self._print(file, f"############### {self._start_tasks.isoformat(' ')} ###############")
        out = {
            FileFormat.PRF_TYPE: FileFormat.PRF_HDR_TYPE,
            FileFormat.PRF_HDR_LABEL: self._label if self._label is not None else "Noname",
            FileFormat.PRF_HDR_BULK: [run_setup._bulk_row, run_setup._bulk_col],
            FileFormat.PRF_HDR_AVIALABLE_CPU: multiprocessing.cpu_count(),
            FileFormat.PRF_HDR_NOW: self._start_tasks.isoformat(' ')
        }
        self._print(file, json.dumps(out))

    def _print_footer(self, file):
        self._print(file,
                    f"############### Duration: {round((datetime.datetime.utcnow() - self._start_tasks).total_seconds(), 1)} seconds ###############")

    def _print_detail(self, file, run_setup: RunSetup, return_dict, processes, threads, group=''):
        sum_time = 0
        sum_deviation = 0
        sum_call = 0
        count = 0

        for return_key in return_dict:
            parallel_ret = return_dict[return_key]
            if (parallel_ret.counter > 0):
                sum_time = sum_time + (parallel_ret.total_duration / parallel_ret.counter)
                sum_deviation += parallel_ret.standard_deviation
                sum_call += parallel_ret.counter
                count += 1
            if (self._detail_output == True):
                self._print(file, f"     {parallel_ret.ToString()}")

        if (count > 0):
            out = {
                FileFormat.PRF_TYPE: FileFormat.PRF_CORE_TYPE,
                FileFormat.PRF_CORE_PLAN_EXECUTOR_ALL: processes * threads,
                FileFormat.PRF_CORE_PLAN_EXECUTOR: [processes, threads],
                FileFormat.PRF_CORE_REAL_EXECUTOR: count,
                FileFormat.PRF_CORE_GROUP: group,
                FileFormat.PRF_CORE_TOTAL_CALL: sum_call,
                FileFormat.PRF_CORE_AVRG_TIME: sum_time / count,
                FileFormat.PRF_CORE_STD_DEVIATION: sum_deviation / count,
                FileFormat.PRF_CORE_TOTAL_CALL_PER_SEC: 0 if (sum_time / count)==0 else (1 / (sum_time / count)) * count * run_setup._bulk_row,
                FileFormat.PRF_CORE_TIME_END: datetime.datetime.utcnow().isoformat(' ')
            }
            self._print(file, f"  {json.dumps(out)}")

    def run_bulk_executor(self,
                              bulk_list= BundleHelper.ROW_1_COL_10_100,
                              executor_list= ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                              run_setup: RunSetup=None,
                              sleep_between_bulks=0):
        """ Run cykle of bulks in cycle of sequences for function execution

        :param bulk_list:           list of bulks for execution in format [[rows, columns], ...]
        :param executor_list:       list of executors for execution in format [[processes, threads], ...]
        :param run_setup:           setup of execution
        :param sleep_between_bulks: sleep between bulks
        """
        for bulk in bulk_list:
            run_setup.set_bulk(bulk[0], bulk[1])

            # execute
            self.run_executor(executor_list, run_setup)
            time.sleep(sleep_between_bulks)
            gc.collect()

    def _open_output(self):
        dirname = os.path.dirname(self._output_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return open(self._output_file, 'a')


    def run_executor(self, executor_list= ExecutorHelper.PROCESS_2_8_THREAD_1_4_SHORT,
                         run_setup: RunSetup=None):
        """ Run executor sequencies

        :param executor_list:       list of executors for execution in format [[processes, threads, 'label'], ...]
        :param run_setup:           setup of execution
        """
        file = None
        print('Execution...')

        try:
            if self._output_file is not None:
                file=self._open_output()

            self._print_header(file, run_setup)

            for executors in executor_list:
                # execution
                with multiprocessing.Manager() as manager:
                    return_dict = manager.dict()
                    self._executeCore(run_setup, return_dict, executors[0], executors[1])
                    self._print_detail(file,
                                       run_setup,
                                       return_dict,
                                       executors[0],
                                       executors[1],
                                       '' if len(executors) <= 2 else executors[2])

            self._print_footer(file)

        except Exception as e:
            self._print(file, str(e) if e is not None else '!! Noname exception !!')
        finally:
            if file is not None:
                file.close()

    def run(self, processes=2, threads=2, run_setup: RunSetup=None):
        """ Run execution of parallel call

        :param processes:       how much processes will be used
        :param threads:         how much threads will be used
        :param run_setup:       setup of execution
        """
        file = None
        print('Execution...')

        try:
            if self._output_file is not None:
                file=self._open_output()

            self._print_header(file, run_setup)
            # Execution
            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                self._executeCore(run_setup, return_dict, processes, threads)
                self._print_detail(file, run_setup, return_dict, processes, threads)
            self._print_footer(file)

        except Exception as e:
            self._print(file, str(e) if e is not None else '!! Noname exception !!')
        finally:
            if file is not None:
                file.close()

    def one_run(self, run_setup: RunSetup=None, parameters=None):
        """ Run test, only one call, execution in new process, with standart write outputs

        :param run_setup:       setting for run
        :param parameters:      parameters for execution, application in case the run_setup is None
        """

        # setup minimalistic values
        if not run_setup:
            run_setup = RunSetup(duration_second=0, start_delay=0, parameters=parameters)

        # run
        self.run(processes=1,
                 threads=1,
                 run_setup=run_setup)

    def init_run(self, run_setup: RunSetup=None, parameters=None, print_output=False):
        """ Init call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file). One new parametr was added '__INIT__': True

        :param parameters:      parameters for execution, application in case the run_setup is None
        :return:                return output from execution
        """

        if run_setup:
            test_parameters = run_setup._parameters.copy() if run_setup._parameters else {}
            test_parameters["__INIT__"] = True
            test_run_setup=RunSetup(duration_second=0, start_delay=0,parameters=test_parameters)
            test_run_setup.set_bulk(run_setup.bulk_row, run_setup.bulk_col)
            return self.test_run(test_run_setup, None, print_output)
        else:
            test_parameters = parameters.copy() if parameters else {}
            test_parameters["__INIT__"] = True
            return self.test_run(None, test_parameters, print_output)

    def test_run(self, run_setup: RunSetup=None, parameters=None, print_output=False):
        """ Test call in current process/thread (without ability to define parallel execution and without
         write standard outputs to file)

        :param run_setup:       setting for run
        :param parameters:      parameters for execution, application in case the run_setup is None
        :return:                return output from execution
        """

        # init
        key="test-no-parallel"
        dictionary={key: ""}
        run_return = RunReturn(key, dictionary)

        if not run_setup:
            run_setup = RunSetup(duration_second=0, start_delay=0, parameters=parameters)
        run_setup.set_start_time()

        # test call
        self._func(run_return, run_setup)

        # return output
        ret=dictionary[key]
        if ret and print_output:
            print(ret.ToString())
        return ret
