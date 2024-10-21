from math import pow
from enum import Flag
from time import perf_counter, perf_counter_ns, sleep
from numpy import random


class GraphScope(Flag):
    """Define typy of graph for generation"""
    off = 1                             # without graph generation
    perf = 2                            # generation of performance graph
    perf_raw = 4                        # generation of performance graph in RAW format
    perf_csv = 8                        # generation of performance graph in RAW format
    perf_csv_raw = 16                   # generation of performance graph in RAW format
    perf_txt = 32                       # generation of performance graph in RAW format
    perf_txt_raw = 64                   # generation of performance graph in RAW format
    exe = 128                           # generation of executor graph
    all_perf = (perf | perf_csv |       # generation of all performance (without raw)
                perf_txt)
    all_perf_raw = (perf_raw |          # generation of all performance (with raw)
                    perf_csv_raw |
                    perf_txt_raw)
    all_no_raw = (perf | perf_csv |
                  perf_txt | exe)       # generation of performance and executor graph (without raw)
    all_raw = (perf_raw |
               perf_csv_raw |
               perf_txt_raw |
               exe)                     # generation of performance and executor graph (with raw)
    all = (perf | perf_raw |
           perf_csv | perf_csv_raw |
           perf_txt | perf_txt_raw |
           exe)                         # generation of performance and executor graph

class BundleHelper:
    """ Predefines values for setting of bundle lists with pattern [[rows, columns], ..] """

    ROW_1_COL_10_100 = [[1, 10], [1, 50], [1, 100]]
    ROW_1_COL_10_1k = [[1, 10], [1, 50], [1, 100], [1, 1000]]
    ROW_1_COL_10_10k = [[1, 10], [1, 50], [1, 100], [1, 1000], [1, 10000]]
    ROW_1_COL_10_100k = [[1, 10], [1, 50], [1, 100], [1, 1000], [1, 10000], [1, 100000]]

    ROW_1_10k_COL_10 = [[1, 10], [100, 10], [1000, 10], [10000, 10]]
    ROW_1_10k_COL_50 = [[1, 50], [100, 50], [1000, 50], [10000, 50]]
    ROW_1_10k_COL_100 = [[1, 100], [100, 100], [1000, 100], [10000, 100]]

    ROW_1_100k_COL_10 = [[1, 10], [100, 10], [1000, 10], [10000, 10], [100000, 10]]
    ROW_1_100k_COL_50 = [[1, 50], [100, 50], [1000, 50], [10000, 50], [100000, 50]]
    ROW_1_100k_COL_100 = [[1, 100], [100, 100], [1000, 100], [10000, 100], [10000, 100]]

class ExecutorHelper:
    """ Predefines values for setting of executor lists with pattern [[processes, threads, label], ...] """

    PROCESS_8_32_THREAD_2_4 = [[8, 2, '2x thread'], [16, 2, '2x thread'], [32, 2, '2x thread'],
                               [8, 4, '4x thread'], [16, 4, '4x thread'], [32, 4, '4x thread']]

    PROCESS_2_8_THREAD_1_4 = [[2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'],
                              [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'],
                              [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread']]

    PROCESS_2_8_THREAD_1_4_SHORT = [[2, 1, '1x thread'], [2, 2, '2x thread'],
                                                         [4, 2, '2x thread'], [4, 4, '4x thread'],
                                                                              [8, 4, '4x thread']]

    PROCESS_2_16_THREAD_1_4 = [[2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'], [16, 1, '1x thread'],
                               [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'], [16, 2, '2x thread'],
                               [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread'], [16, 4, '4x thread']]

    PROCESS_1_8_THREAD_1 = [[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread']]
    PROCESS_1_8_THREAD_2 = [[1, 2, '2x thread'], [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread']]
    PROCESS_1_8_THREAD_4 = [[1, 4, '4x thread'], [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread']]
    PROCESS_1_8_THREAD_8 = [[1, 8, '8x thread'], [2, 8, '8x thread'], [4, 8, '8x thread'], [8, 8, '8x thread']]

    PROCESS_1_16_THREAD_1 = [[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'],
                             [16, 1, '1x thread']]
    PROCESS_1_16_THREAD_2 = [[1, 2, '2x thread'], [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'],
                             [16, 2, '2x thread']]
    PROCESS_1_16_THREAD_4 = [[1, 4, '4x thread'], [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread'],
                             [16, 4, '4x thread']]
    PROCESS_1_16_THREAD_8 = [[1, 8, '8x thread'], [2, 8, '8x thread'], [4, 8, '8x thread'], [8, 8, '8x thread'],
                             [16, 8, '8x thread']]

    PROCESS_1_32_THREAD_1 = [[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'],
                             [16, 1, '1x thread'], [32, 1, '1x thread']]
    PROCESS_1_32_THREAD_2 = [[1, 2, '2x thread'], [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'],
                             [16, 2, '2x thread'], [32, 2, '2x thread']]
    PROCESS_1_32_THREAD_4 = [[1, 4, '4x thread'], [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread'],
                             [16, 4, '4x thread'], [32, 4, '4x thread']]
    PROCESS_1_32_THREAD_8 = [[1, 8, '8x thread'], [2, 8, '8x thread'], [4, 8, '8x thread'], [8, 8, '8x thread'],
                             [16, 8, '8x thread'], [32, 8, '8x thread']]

    PROCESS_1_64_THREAD_1 = [[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'],
                             [16, 1, '1x thread'], [32, 1, '1x thread'], [64, 1, '1x thread']]
    PROCESS_1_64_THREAD_2 = [[1, 2, '2x thread'], [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'],
                             [16, 2, '2x thread'], [32, 2, '2x thread'], [64, 2, '2x thread']]
    PROCESS_1_64_THREAD_4 = [[1, 4, '4x thread'], [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread'],
                             [16, 4, '4x thread'], [32, 4, '4x thread'], [64, 4, '4x thread']]
    PROCESS_1_64_THREAD_8 = [[1, 8, '8x thread'], [2, 8, '8x thread'], [4, 8, '8x thread'], [8, 8, '8x thread'],
                             [16, 8, '8x thread'], [32, 8, '8x thread'], [64, 8, '8x thread']]

    PROCESS_1_128_THREAD_1 = [[1, 1, '1x thread'], [2, 1, '1x thread'], [4, 1, '1x thread'], [8, 1, '1x thread'],
                              [16, 1, '1x thread'], [32, 1, '1x thread'], [64, 1, '1x thread'], [128, 1, '1x thread']]
    PROCESS_1_128_THREAD_2 = [[1, 2, '2x thread'], [2, 2, '2x thread'], [4, 2, '2x thread'], [8, 2, '2x thread'],
                              [16, 2, '2x thread'], [32, 2, '2x thread'], [64, 2, '2x thread'], [128, 2, '2x thread']]
    PROCESS_1_128_THREAD_4 = [[1, 4, '4x thread'], [2, 4, '4x thread'], [4, 4, '4x thread'], [8, 4, '4x thread'],
                              [16, 4, '4x thread'], [32, 4, '4x thread'], [64, 4, '4x thread'], [128, 4, '4x thread']]
    PROCESS_1_128_THREAD_8 = [[1, 8, '8x thread'], [2, 8, '8x thread'], [4, 8, '8x thread'], [8, 8, '8x thread'],
                              [16, 8, '8x thread'], [32, 8, '8x thread'], [64, 8, '8x thread'], [128, 8, '8x thread']]

    def grow_thread(label_thread=True, process=2, thread_pow_start=1, thread_pow_stop=6):
        """
        Generate sequence of executors, number of processes are stable, and
        number of thread grow from 2^thread_pow_start to 2^thread_pow_stop

        :param label_thread:        label for executors
        :param process:             stable number of processes
        :param thread_pow_start:    start number of thread from 2^thread_pow_start
        :param thread_pow_stop:     stop number of thread to 2^thread_pow_stop
        :return:                    executor sequence e.g.
                                    "[[2, 2, '2x thread'], [2, 4, '4x thread'], [2, 8, '8x thread'], ...]"
        """
        pattern = []
        for i in range(thread_pow_start, thread_pow_stop):
            added = int(pow(2, i))
            label = f"{added}x thread" if label_thread else f"{process}x process"
            pattern.append([process, added, label])
        return pattern

    def grow_process(label_process=True, thread=2, process_pow_start=1, process_pow_stop=6):
        """
        Generate sequence of executors, number of threads are stable, and
        number of thread grow from 2^process_pow_start to 2^process_pow_stop

        :param label_process:       label for executors
        :param thread:              stable number of threads
        :param process_pow_start:   start number of process from 2^process_pow_start
        :param process_pow_stop:    stop number of thread to 2^process_pow_stop
        :return:                    executor sequence e.g.
                                    "[[2, 2, '2x process'], [4, 2, '4x process'], [8, 2, '8x process'], ...]"
        """
        pattern = []
        for i in range(process_pow_start, process_pow_stop):
            added = int(pow(2, i))
            label = f"{added}x process" if label_process else f"{thread}x thread"
            pattern.append([added, thread, label])
        return pattern


def get_rng_generator(complex_init = True) -> random._generator.Generator:
    """Create generator of random values with initiation"""

    # now and now_ms (as detail about milliseconds)
    now = perf_counter()
    now_ms = (now - int(now)) * 1000000000

    # calc based on CPU speed
    ns_start = perf_counter_ns()
    if complex_init:
        sleep(0.001)
        ns_stop = perf_counter_ns()

        # create generator with more random seed (now, now_ms, cpu speed)
        return random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])
    else:
        return random.default_rng([int(now), int(now_ms), ns_start])
