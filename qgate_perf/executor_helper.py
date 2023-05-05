import math

class ExecutorHelper:
    """ Predefines values for setting of executor lists with pattern [[processes, threads, label], ..] """
    def __init__(self):
        pass

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

    def ThreadGrow(label_thread=True, process=2, thread_pow_start=1, thread_pow_stop=6):
        pattern = []
        for i in range(thread_pow_start, thread_pow_stop):
            added = int(math.pow(2, i))
            label = f"{added}x thread" if label_thread else f"{process}x process"
            pattern.append([process, added, label])
        return pattern

    def ProcesGrow(label_process=True, process_pow_start=1, process_pow_stop=6, thread=2):
        pattern = []
        for i in range(process_pow_start, process_pow_stop):
            added = int(math.pow(2, i))
            label = f"{added}x process" if label_process else f"{thread}x thread"
            pattern.append([added, thread, label])
        return pattern

