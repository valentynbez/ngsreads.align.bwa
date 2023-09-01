from bwalib.bwa cimport bwa_idx_build
from bwalib.utils cimport cpu_time

def bwa_index(fa, prefix, algo_type=0, block_size=10e9):
    return bwa_idx_build(fa, prefix, algo_type, block_size)

def _cpu_time():
    return _cpu_time()