import datetime
import glob
import unittest
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import GraphScope
import time
from os import path
import shutil
import numpy


def prf_test(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    generator = numpy.random.default_rng()

    # init (contain executor synchonization, if needed)
    probe = ParallelProbe(run_setup)

    if run_setup.is_init:
        print(f"!!! INIT CALL !!!   {run_setup.bulk_row} x {run_setup.bulk_col}")
        return None

    while True:

        # START - performance measure for specific part of code
        probe.start()

        for r in range(run_setup.bulk_row * run_setup.bulk_col):
            time.sleep(0.001)

        # STOP - performance measure specific part of code
        if probe.stop():
            break

    # generate exception
    gen_err=run_setup.param("generate_error")
    if gen_err =="yes":
        raise Exception('Simulated exception')
    elif gen_err == "random":
        if generator.integers(0,5)==0:
            raise Exception('Random exception')

    return probe

class TestCaseGraph(unittest.TestCase):
    OUTPUT_ADR = "../output/test_graph/"

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TestCaseGraph.OUTPUT_ADR, True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_graph(self):
        generator = ParallelExecutor(prf_test,
                                     label="test_aus_ger",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setup = RunSetup(duration_second=4, start_delay=2, parameters=None)
        self.assertTrue(generator.run_bulk_executor([[10, 10], [100, 10]],
                                                    [[1, 2, 'Austria perf'], [2, 2, 'Austria perf'], [4, 2, 'Austria perf'],
                                                    [1, 4, 'Germany perf'], [2, 4, 'Germany perf'], [4, 4, 'Germany perf']],
                                                    setup))
        generator.create_graph(self.OUTPUT_ADR)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_aus_ger-*-bulk-10x10.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_aus_ger-*-bulk-100x10.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def test_graph_run_exception(self):
        generator = ParallelExecutor(prf_test,
                                     label="test_exception",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run(1,1, setup))
        generator.create_graph(self.OUTPUT_ADR)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_exception-*-bulk-1x1.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def test_graph_runexecutor_exception(self):
        generator = ParallelExecutor(prf_test,
                                     label="test_exception2",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        self.assertFalse(generator.run_executor([[2,2]], setup))
        generator.create_graph(self.OUTPUT_ADR)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_exception2-*-bulk-1x1.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

        # TODO: add assert for these two tests
        generator.create_graph_perf(self.OUTPUT_ADR)
        generator.create_graph_exec(self.OUTPUT_ADR)


    def test_graph_runbulkexecutor_exception_random(self):
        generator = ParallelExecutor(prf_test,
                                     label="test_random",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test_random.txt"))

        setting = {"generate_error": "random"}

        setup=RunSetup(duration_second=4, start_delay=2, parameters=setting)
        generator.run_bulk_executor([[1,1], [1,5]], [[4,4],[8,4],[16,4]], setup)
        generator.create_graph(self.OUTPUT_ADR)

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # check relevant files
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_random-*-bulk-1x1.png"))
        self.assertTrue(len(file)==2)
        print(file[0])

        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_random-*-bulk-1x5.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def test_graph_scope(self):
        generator = ParallelExecutor(prf_test,
                                     label="test_graph_scope",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test_graph_scope.txt"))

        setup = RunSetup(duration_second=1, start_delay=2, parameters=None)
        self.assertTrue(generator.run_bulk_executor([[10, 10]],
                                                    [[1, 2, 'Austria perf'],
                                                    [1, 4, 'Germany perf']],
                                                    setup))
        generator.create_graph(self.OUTPUT_ADR, GraphScope.perf)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "1 sec", today, f"PRF-test_graph_scope-*-bulk-10x10.png"))
        self.assertTrue(len(file) == 1)
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-exec", "1 sec", today, f"EXE-test_graph_scope-*-bulk-10x10-*.png"))
        self.assertTrue(len(file) == 0) # without these file


        generator.create_graph(self.OUTPUT_ADR, GraphScope.perf_raw)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "1 sec", today, f"PRF-test_graph_scope-RAW-*-bulk-10x10.png"))
        self.assertTrue(len(file) == 1)
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-exec", "1 sec", today, f"EXE-test_graph_scope-*-bulk-10x10-*.png"))
        self.assertTrue(len(file) == 0) # without these file


        generator.create_graph(self.OUTPUT_ADR, GraphScope.exe)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-exec", "1 sec", today, f"EXE-test_graph_scope-*-bulk-10x10-*.png"))
        self.assertTrue(len(file) == 2)
