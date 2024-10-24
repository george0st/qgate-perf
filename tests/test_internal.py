import os
import unittest
import logging
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.helper import get_readable_duration #ExecutorHelper, get_readable_duration
from qgate_perf.run_return import RunReturn
from qgate_perf.standard_deviation import StandardDeviation
from pympler import asizeof
import time
from os import path
import shutil


class TestCaseInternal(unittest.TestCase):
    """Only small internal checks"""
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

    def test_size(self):
        import sys

        setup=RunSetup(20,0)
        probe = ParallelProbe(None)
        dev = StandardDeviation(0)

        # print size of data
        print('ParallelProbe size: ' + str(round(sys.getsizeof(probe) / (1024 * 1024), 2)) + '/' + \
              str(round(sys.getsizeof(probe) / (1024), 2)) + '/' + \
              str(sys.getsizeof(probe)) + ' [MB/KB/B]')
        print('ParallelProbe size: ' + str(round(asizeof.asizeof(probe) / (1024 * 1024), 2)) + '/' + \
              str(round(asizeof.asizeof(probe) / (1024), 2)) + '/' + \
              str(asizeof.asizeof(probe)) + ' [MB/KB/B]')

        print(asizeof.asized(probe, detail=5).format())
        #print(asizeof.asizeof(probe, detail=1).format())


        print('StandardDeviation size: ' + str(round(sys.getsizeof(dev) / (1024 * 1024), 2)) + '/' + \
              str(round(sys.getsizeof(dev) / (1024), 2)) + '/' + \
              str(sys.getsizeof(dev)) + ' [MB/KB/B]')
        print('StandardDeviation size: ' + str(round(asizeof.asizeof(dev) / (1024 * 1024), 2)) + '/' + \
              str(round(asizeof.asizeof(dev) / (1024), 2)) + '/' + \
              str(asizeof.asizeof(dev)) + ' [MB/KB/B]')

    def test_readable_time(self):
        exec = ParallelExecutor(None)

        print(get_readable_duration(100))
        print(get_readable_duration(100.45))
        print(get_readable_duration(5004.45))

    def test_precison(self):
        text_format="{:<05}"

        print(text_format.format(round(810.1234567,4)))
        print(text_format.format(round(0.12, 4)))