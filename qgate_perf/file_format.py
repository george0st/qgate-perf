
class FileFormat:

    PRF_TYPE = "type"

    # header
    PRF_HDR_TYPE = "headr"
    PRF_HDR_LABEL = "label"
    PRF_HDR_BULK = "bulk"
    PRF_HDR_DURATION = "duration"
    PRF_HDR_AVIALABLE_CPU = "cpu"
    PRF_HDR_HOST = "host"
    PRF_HDR_MEMORY = "mem"
    PRF_HDR_MEMORY_FREE = "mem_free"
    PRF_HDR_NOW = "now"
        # header for HUMAN
    HR_PRF_HDR_LABEL = "lbl"
    HR_PRF_HDR_MEMORY = "mem/free"

    # detail
    PRF_DETAIL_TYPE = "detail"
    PRF_DETAIL_PROCESSID = "processid"
    PRF_DETAIL_CALLS = "calls"
    PRF_DETAIL_COUNT = "count"
    PRF_DETAIL_TOTAL = "total"
    PRF_DETAIL_AVRG = "avrg"
    PRF_DETAIL_MIN = "min"
    PRF_DETAIL_MAX = "max"
    PRF_DETAIL_STDEV = "st-dev"
    PRF_DETAIL_ERR = "err"
    PRF_DETAIL_TIME_INIT = "initexec"
    PRF_DETAIL_TIME_START = "startexec"
    PRF_DETAIL_TIME_END = "endexec"
        # detail for HUMAN
    HR_PRF_DETAIL_CALLS = "call"
    HR_PRF_DETAIL_AVRG = "avr"
    HR_PRF_DETAIL_STDEV = "std"
    HR_PRF_DETAIL_TOTAL = "tduration"

    # core output
    PRF_CORE_TYPE = "core"
    PRF_CORE_PLAN_EXECUTOR_ALL = "plan_executors"
    PRF_CORE_PLAN_EXECUTOR = "plan_executors_detail"
    PRF_CORE_REAL_EXECUTOR = "real_executors"
    PRF_CORE_GROUP = "group"
    PRF_CORE_TOTAL_CALL = "total_calls"
    PRF_CORE_AVRG_TIME = "avrg_time"
    PRF_CORE_STD_DEVIATION = "std_deviation"
    PRF_CORE_TOTAL_CALL_PER_SEC = "total_call_per_sec"              # total raw performance and multiply by rows in bundle
    PRF_CORE_TOTAL_CALL_PER_SEC_RAW = "total_call_per_sec_raw"      # total raw performance (calls per one second)
    PRF_CORE_TIME_END = "endexec"
        # core output for HUMAN
    HM_PRF_CORE_PLAN_EXECUTOR_ALL = "plan"
    HM_PRF_CORE_REAL_EXECUTOR = "exec"
    HM_PRF_CORE_GROUP = "grp"
    HM_PRF_CORE_TOTAL_CALL = "call"
    HM_PRF_CORE_TOTAL_CALL_PER_SEC = "callsec"                      # total raw performance and multiply by rows in bundle
    HM_PRF_CORE_TOTAL_CALL_PER_SEC_RAW = "callsec_raw"              # total raw performance (calls per one second)
    HM_PRF_CORE_AVRG_TIME = "avr"
    HM_PRF_CORE_STD_DEVIATION = "std"
