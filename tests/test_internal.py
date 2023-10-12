import os
import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
from qgate_perf.run_return import RunReturn
from qgate_perf.bundle_helper import BundleHelper
from qgate_perf.executor_helper import ExecutorHelper
import time
from os import path
import shutil


class TestCaseInternal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_run_setup(self):
        setup=RunSetup(20,2,{"port":1034, "server": "10.192.0.12"})

        print(f"Port: {setup['port']}")
        self.assertIsNotNone(setup['port'])

        print(f"Port: {setup.param('ip')}")
        self.assertIsNone(setup['ip'])

        print(f"Port: {setup.param('ip','localhost')}")
        self.assertIsNotNone(setup.param('ip','localhost'))

        print(setup['port'])
        self.assertIsNotNone(setup['port'])

        print(1000+setup['port'])
        self.assertIsNotNone(1000+setup['port'])

        print(str(setup))
        self.assertIsNotNone(str(setup))



