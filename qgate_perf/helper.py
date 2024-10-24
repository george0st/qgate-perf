from math import pow
from enum import Flag
from time import perf_counter, perf_counter_ns, sleep
from numpy import random
from contextlib import suppress


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

class ExecutorHelper:
    """ Predefines values for setting of executor lists with pattern [[processes, threads, label], ...] """

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

class Singleton (type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

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

def get_memory():

    mem_total, mem_free = "", ""
    with suppress(Exception):
        import psutil

        values=psutil.virtual_memory()
        mem_total=f"{round(values.total/(1073741824),1)} GB"
        mem_free=f"{round(values.free/(1073741824),1)} GB"
    return mem_total, mem_free

def get_host():
    """ Return information about the host in format (host_name/ip addr)"""

    host = ""
    with suppress(Exception):
        import socket

        host_name=socket.gethostname()
        ip=socket.gethostbyname(host_name)
        host=f"{host_name}/{ip}"
    return host

def get_readable_duration(duration_seconds):
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
