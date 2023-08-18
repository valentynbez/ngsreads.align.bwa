from bwalib.bwa cimport bwa_idx_build

def bwa_index(fa, prefix, algo_type=0, block_size=10e9):
    return bwa_idx_build(fa, prefix, algo_type, block_size)