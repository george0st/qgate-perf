from qgate_perf.parallel_executor import ParallelExecutor, InitCallSetting
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from qgate_perf.run_return import RunReturn

import click
import logging
import time

def prf_GIL_impact(run_return: RunReturn, run_setup: RunSetup):
    """ Function for performance testing"""
    try:
        # INIT - contain executor synchonization, if needed
        probe=ParallelProbe(run_setup)

        if run_setup.is_init:
            print(f"!!!!!!!!!!!!!!!   {run_setup.bulk_row} x {run_setup.bulk_col}")

        while (True):

            # START - probe, only for this specific code part
            probe.start()

            for r in range(run_setup.bulk_row * run_setup.bulk_col):
                time.sleep(0.001)

            # STOP - probe
            if probe.stop():
                break

        # RETURN - data from probe
        run_return.probe=probe

    except Exception as ex:
        # RETURN - error
        run_return.probe=ParallelProbe(None, ex)



@click.command()
@click.option("--input", help="input directory (default is directory 'input')", default="input")
@click.option("--output", help="output directory (default is directory 'output')", default="output")
def graph(input,output):
    """Generate graphs based in input data."""
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    generator = ParallelExecutor(prf_GIL_impact,
                                 label="GIL_impact",
                                 detail_output=True,
                                 output_file="output/prf_calc3.txt",init_call=InitCallSetting.EachBundle)



#    generator.one_shot()
#    generator.test_call(RunSetup(duration_second=5, start_delay=0))
#    generator.run_executor([[10,2,'xxxx'],[5,1,'sss']], RunSetup(duration_second=5, start_delay=5))

#     generator.run_executor([[16,1,'calc'],[16,2,'calc'],[64,1,'calc'],[64,2,'calc'],[64,4,'calc'],[128,4,'calc']],
#                            RunSetup(duration_second=5, start_delay=20))

    generator.run_bulk_executor([[1,1],[1,20]],[[16,1,'calc'],[16,2,'calc'],[64,1,'calc'],[64,2,'calc'],[64,4,'calc'],[128,4,'calc']],
                           RunSetup(duration_second=5, start_delay=20))

    # generator.run_bulk_executor(bulk_list=[[1, 1]],
    #                             executor_list=[[4, 1,'1x thread'],[8, 1,'1x thread'],[16, 1, '1x thread'],
    #                                            [4, 2, '2x threads'], [8, 2, '2x threads'],
    #                                            [4, 4, '4x threads']],
    #                             run_setup=RunSetup(duration_second=5, start_delay=0))


if __name__ == '__main__':
    graph()