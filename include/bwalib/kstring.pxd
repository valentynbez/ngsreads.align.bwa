cdef extern from "kstring.h" nogil:
    ctypedef struct kstring_t:
        size_t l, m
        char *s

