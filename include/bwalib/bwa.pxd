cdef extern from "bwa.h":
    cdef int bwa_idx_build(char *fa, char *prefix,
                           int algo_type, int block_size)