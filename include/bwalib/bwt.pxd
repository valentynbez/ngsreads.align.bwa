cdef extern from "bwt.h" nogil:
    cdef struct bwt_t:
        int primary     # S^{-1}(0), or the primary index of BWT
        int L2[5]       # C(), cumulative count
        int seq_len     # sequence length
        int bwt_size    # size of bwt, about seq_len/4
        int *bwt        # bwt
        # occurance array, separated to two parts
        int cnt_table[256]
        # suffix array
        int sa_intv
        int n_sa
        int *sa
