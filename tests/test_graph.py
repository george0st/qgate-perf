from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.helper import GraphScope
from os import path
import datetime
import glob
import unittest
import time
import shutil
import numpy


def prf_test(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""

    generator = numpy.random.default_rng()

    # init (contain executor synchronization, if needed)
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
        """Basic test"""
        generator = ParallelExecutor(prf_test,
                                     label="test_aus_ger",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setup = RunSetup(duration_second=4, start_delay=0, parameters=None)
        self.assertTrue(generator.run_bulk_executor([[10, 10], [100, 10]],
                                                    [[1, 2, 'Austria perf'], [2, 2, 'Austria perf'], [4, 2, 'Austria perf'],
                                                    [1, 4, 'Germany perf'], [2, 4, 'Germany perf'], [4, 4, 'Germany perf']],
                                                    setup).state)
        generator.create_graph(self.OUTPUT_ADR, scope = GraphScope.perf | GraphScope.perf_raw)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_aus_ger-*-bulk-10x10.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_aus_ger-*-bulk-100x10.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def test_graph_run_exception(self):
        """Simply run and exceptions"""
        generator = ParallelExecutor(prf_test,
                                     label="test_exception",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=0, parameters=setting)
        self.assertFalse(generator.run(1,1, setup).state)
        generator.create_graph(self.OUTPUT_ADR, scope = GraphScope.perf | GraphScope.perf_raw)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_exception-*-bulk-1x1.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def test_graph_runexecutor_exception(self):
        """Executor list and exceptions"""
        generator = ParallelExecutor(prf_test,
                                     label="test_exception2",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test.txt"))

        setting = {"generate_error": "yes"}

        setup=RunSetup(duration_second=4, start_delay=0, parameters=setting)
        self.assertFalse(generator.run_executor([[2,2]], setup).state)
        generator.create_graph(self.OUTPUT_ADR, scope = GraphScope.perf | GraphScope.perf_raw)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_exception2-*-bulk-1x1.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

        # TODO: add assert for these two tests
        generator.create_graph_perf(self.OUTPUT_ADR)
        generator.create_graph_exec(self.OUTPUT_ADR)


    def test_graph_runbulkexecutor_exception_random(self):
        """Bulk bundles and executor list with executions"""
        generator = ParallelExecutor(prf_test,
                                     label="test_random",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test_random.txt"))

        setting = {"generate_error": "random"}

        setup=RunSetup(duration_second=4, start_delay=0, parameters=setting)
        generator.run_bulk_executor([[1,1], [1,5]], [[4,4],[8,4],[16,4]], setup)
        generator.create_graph(self.OUTPUT_ADR, scope = GraphScope.perf | GraphScope.perf_raw)

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # check relevant files
        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_random-*-bulk-1x1.png"))
        self.assertTrue(len(file)==2)
        print(file[0])

        file=glob.glob(path.join(self.OUTPUT_ADR, "graph-perf", "4 sec", today, f"PRF-test_random-*-bulk-1x5.png"))
        self.assertTrue(len(file) == 2)
        print(file[0])

    def _generic_scope(self, scope="perf", amount = 1, name_contain = ["PRF-"], name_not_contain = "RAW"):
        generator = ParallelExecutor(prf_test,
                                     label="test_graph_scope",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, f"perf_{scope.lower()}_graph_scope.txt"))

        setup = RunSetup(duration_second=1, start_delay=0, parameters=None)
        self.assertTrue(generator.run_bulk_executor([[1, 1]],
                                                    [[1, 1, 'Austria perf'], [2, 1, 'Austria perf']],
                                                    setup).state)
        output_dir = path.join(self.OUTPUT_ADR, "scope", scope)
        generator.create_graph(output_dir, GraphScope[scope.lower()])

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if scope.lower() != "exe":
            files=glob.glob(path.join(output_dir, "graph-perf", "1 sec", today, f"*.*"))
        else:
            files = glob.glob(path.join(output_dir, "graph-exec", "1 sec", today, f"*.*"))
        self.assertTrue(len(files) == amount)
        for file in files:
            for itm in name_contain:
                self.assertTrue(file.find(itm) != -1)
            if name_not_contain:
                self.assertTrue(file.find(name_not_contain) == -1)

    def test_graph_scope_perf(self):
        """Test scope with Perf"""
        self._generic_scope("perf", 1, ["PRF-"], "RAW")

    def test_graph_scope_perf_raw(self):
        """Test scope with Perf raw"""
        self._generic_scope("perf_raw", 1, ["PRF-", "RAW"], None)

    def test_graph_scope_txt(self):
        """Test scope with TXT"""
        self._generic_scope("perf_txt", 1, ["TXT-"], "RAW")

    def test_graph_scope_txt_raw(self):
        """Test scope with TXT raw"""
        self._generic_scope("perf_txt_raw", 1, ["TXT-","RAW"], None)

    def test_graph_scope_csv(self):
        """Test scope with CSV"""
        self._generic_scope("perf_csv", 1, ["CSV-"], "RAW")

    def test_graph_scope_csv_raw(self):
        """Test scope with CSV raw"""
        self._generic_scope("perf_csv_raw", 1, ["CSV-", "RAW"], None)

    def test_graph_scope_exe(self):
        """Test scope with Exe"""
        self._generic_scope("exe", 2, ["EXE-"], "RAW")

    def test_graph_percentile(self):

        generator = ParallelExecutor(prf_test,
                                     label="test_percentile",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test_percentile.txt"))

        setup=RunSetup(duration_second=2, start_delay=0, parameters={"percentile": 0.95})
        generator.run_bulk_executor([[1,1], [1,5]], [[4,4],[8,4],[16,4]], setup)
        output=generator.create_graph_perf(self.OUTPUT_ADR)
        self.assertTrue(len(output)==2)

    def test_graph_onlynew(self):

        generator = ParallelExecutor(prf_test,
                                     label="test_percentile",
                                     detail_output=True,
                                     output_file=path.join(self.OUTPUT_ADR, "perf_test_only_new.txt"))

        setup=RunSetup(duration_second=2, start_delay=0, parameters={"percentile": 0.95})
        generator.run_bulk_executor([[1,1]], [[1,1]], setup)

        output=generator.create_graph_perf(path.join(self.OUTPUT_ADR, "only_new"), only_new = True)
        self.assertTrue(len(output) == 1)

        output=generator.create_graph_perf(path.join(self.OUTPUT_ADR, "only_new"), only_new = True)
        self.assertTrue(len(output) == 0)

