cdef extern from "ksw.h" nogil:
    cdef struct kswr_t:
        int score        # best score
        int target_end
        int query_end
        int score2
        int target_end2
        int target_begin
        int query_begin
