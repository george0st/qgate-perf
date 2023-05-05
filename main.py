from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_return import ParallelReturn
from qgate_perf.run_setup import RunSetup
from qgate_perf.executor_helper import ExecutorHelper
import click
import logging
import time


def prf_GIL_impact(return_key, return_dict, run_setup: RunSetup):
    """ Function for performance testing"""
    try:
        # INIT - contain executor synchonization, if needed
        performance = ParallelReturn(run_setup)

        while (True):

            # START - performance test, only for this specific code part
            performance.start()

            for r in range(run_setup.bulk_row * run_setup.bulk_col):
                time.sleep(0)

            # STOP - performance test
            if performance.stop():
                break

        # RETURN - data from performance
        return_dict[return_key] = performance
    except Exception as ex:
        # RETURN - error
        return_dict[return_key] = ParallelReturn(None, ex)

@click.command()
@click.option("--input", help="input directory (default is directory 'input'", default="input")
@click.option("--output", help="output directory (default is directory 'output'", default="output")
def graph(input,output):
    """Generate graphs based in input data."""
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    generator = ParallelExecutor(prf_GIL_impact,
                                 label="GIL_impact",
                                 detail_output=True,
                                 output_file="output/prf_gil_impact_test.txt")


    generator.one_shot()
#    generator.test_call(RunSetup(duration_second=5, start_delay=0))
#    generator.run_executor([[1,1,'xxxx']], RunSetup(duration_second=5, start_delay=0))
    # generator.run_bulk_executor(bulk_list=[[1, 1]],
    #                             executor_list=[[4, 1,'1x thread'],[8, 1,'1x thread'],[16, 1, '1x thread'],
    #                                            [4, 2, '2x threads'], [8, 2, '2x threads'],
    #                                            [4, 4, '4x threads']],
    #                             run_setup=RunSetup(duration_second=5, start_delay=0))


if __name__ == '__main__':
    graph()