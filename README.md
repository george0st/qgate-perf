[![PyPI version fury.io](https://badge.fury.io/py/qgate-perf.svg)](https://pypi.python.org/pypi/qgate-perf/)
# QGate-Perf

Performance test generator part of Quality Gate.

## Usage

```lang-python
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_return import ParallelReturn
from qgate_perf.run_setup import RunSetup
import time

# Function for performance testing
def prf_GIL_impact(return_key, return_dict, run_setup: RunSetup):
    try:
        # init (contain executor synchonization, if needed)
        performance=ParallelReturn(run_setup)

        while(True):
        
            # START - performance measure for specific part of code
            performance.start()

            for r in range(run_setup.bulk_row * run_setup.bulk_col):
                time.sleep(0)

            # STOP - performance measure specific part of code
            if performance.stop():
                break

        # return outputs
        if return_dict is not None:
            return_dict[return_key] = performance

    except Exception as ex:
        # return outputs in case of error
        if return_dict is not None:
            return_dict[return_key] = ParallelReturn(None, ex)


generator = ParallelExecutor(prf_GIL_impact,
                             label="GIL_impact",
                             detail_output=True,
                             output_file="prf_gil_impact_01.txt")

generator.run_bulk_executor(bulk_list=[[1, 1]],
                            executor_list=[[16, 1, '1x thread'], [8, 2, '2x threads'],[4, 4,'4x threads']],
                            run_setup=RunSetup(duration_second=20,start_delay=0))
```

# Outputs in text file
```
############### 2023-05-05 06:30:36.194849 ###############
{"type": "headr", "label": "GIL_impact", "bulk": [1, 1], "available_cpu": 12, "now": "2023-05-05 06:30:36.194849"}
  {"type": "core", "plan_executors": 4, "plan_executors_detail": [4, 1], "real_executors": 4, "group": "1x thread", "total_calls": 7590439, "avrg_time": 1.4127372338382197e-06, "std_deviation": 3.699171006877347e-05, "total_call_per_sec": 2831382.8673804617, "endexec": "2023-05-05 06:30:44.544829"}
  {"type": "core", "plan_executors": 8, "plan_executors_detail": [8, 1], "real_executors": 8, "group": "1x thread", "total_calls": 11081697, "avrg_time": 1.789265660825848e-06, "std_deviation": 4.164309967620533e-05, "total_call_per_sec": 4471107.994274894, "endexec": "2023-05-05 06:30:52.623666"}
  {"type": "core", "plan_executors": 16, "plan_executors_detail": [16, 1], "real_executors": 16, "group": "1x thread", "total_calls": 8677305, "avrg_time": 6.2560950624827455e-06, "std_deviation": 8.629422798757681e-05, "total_call_per_sec": 2557505.8946835063, "endexec": "2023-05-05 06:31:02.875799"}
  {"type": "core", "plan_executors": 8, "plan_executors_detail": [4, 2], "real_executors": 8, "group": "2x threads", "total_calls": 2761851, "avrg_time": 1.1906723084757647e-05, "std_deviation": 0.00010741937495211329, "total_call_per_sec": 671889.3135459893, "endexec": "2023-05-05 06:31:10.283786"}
  {"type": "core", "plan_executors": 16, "plan_executors_detail": [8, 2], "real_executors": 16, "group": "2x threads", "total_calls": 3605920, "avrg_time": 1.858694254439209e-05, "std_deviation": 0.00013301637613377212, "total_call_per_sec": 860819.3607844017, "endexec": "2023-05-05 06:31:18.740831"}
  {"type": "core", "plan_executors": 16, "plan_executors_detail": [4, 4], "real_executors": 16, "group": "4x threads", "total_calls": 1647508, "avrg_time": 4.475957498576462e-05, "std_deviation": 0.00020608402170105327, "total_call_per_sec": 357465.41393855185, "endexec": "2023-05-05 06:31:26.008649"}
############### Duration: 49.9 seconds ###############
```

# Outputs in text file with detail
```
############### 2023-05-05 07:01:18.571700 ###############
{"type": "headr", "label": "GIL_impact", "bulk": [1, 1], "available_cpu": 12, "now": "2023-05-05 07:01:18.571700"}
     {"type": "detail", "processid": 12252, "calls": 1896412, "total": 2.6009109020233154, "avrg": 1.371490426143325e-06, "min": 0.0, "max": 0.0012514591217041016, "st-dev": 3.6488665183545995e-05, "initexec": "2023-05-05 07:01:21.370528", "startexec": "2023-05-05 07:01:21.370528", "endexec": "2023-05-05 07:01:26.371062"}
     {"type": "detail", "processid": 8944, "calls": 1855611, "total": 2.5979537963867188, "avrg": 1.4000530264084008e-06, "min": 0.0, "max": 0.001207590103149414, "st-dev": 3.6889275786419565e-05, "initexec": "2023-05-05 07:01:21.466496", "startexec": "2023-05-05 07:01:21.466496", "endexec": "2023-05-05 07:01:26.466551"}
     {"type": "detail", "processid": 2108, "calls": 1943549, "total": 2.6283881664276123, "avrg": 1.3523652691172758e-06, "min": 0.0, "max": 0.0012514591217041016, "st-dev": 3.624462003401045e-05, "initexec": "2023-05-05 07:01:21.709203", "startexec": "2023-05-05 07:01:21.709203", "endexec": "2023-05-05 07:01:26.709298"}
     {"type": "detail", "processid": 19292, "calls": 1973664, "total": 2.6392557621002197, "avrg": 1.3372366127670262e-06, "min": 0.0, "max": 0.0041027069091796875, "st-dev": 3.620965943471147e-05, "initexec": "2023-05-05 07:01:21.840541", "startexec": "2023-05-05 07:01:21.840541", "endexec": "2023-05-05 07:01:26.841266"}
  {"type": "core", "plan_executors": 4, "plan_executors_detail": [4, 1], "real_executors": 4, "group": "1x thread", "total_calls": 7669236, "avrg_time": 1.3652863336090071e-06, "std_deviation": 3.645805510967187e-05, "total_call_per_sec": 2929788.3539391863, "endexec": "2023-05-05 07:01:26.891144"}
  ...
```

# Next outputs generated from addition package qgate-graph

![graph](https://fivekg.onrender.com/images/qgate/PRF-NoSQL_igz_nonprod-2023-04-23_14-41-18-bulk-100x50.png)
![graph](https://fivekg.onrender.com/images/qgate/EXE-NoSQL-2023-05-04_19-33-30-bulk-1x50-plan-8x2.png)

