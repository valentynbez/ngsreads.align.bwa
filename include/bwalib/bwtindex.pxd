from bwalib.bwt cimport bwt_t

cdef extern from "bwtindex.c" nogil:
    cdef bwt_t* bwt_pac2bwt(const char* fn_pac, int use_is)
