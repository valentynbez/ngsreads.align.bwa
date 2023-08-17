from libc.stdio cimport FILE

cdef extern from "bntseq.h" nogil:
    cdef struct bntann1_t:
        int offset
        int len
        int n_ambs
        int n_ambs
        int gi
        int is_alt
        char* name
        char* anno

    cdef struct bntamb1_t:
        int offset
        int len
        char amb

    cdef struct bntseq_t:
        int l_pac
        int n_seqs
        int seed
        bntann1_t *anns  # n_seqs elements
        int n_holes
        bntamb1_t *ambs  # n_holes elements
        FILE *fp_pac