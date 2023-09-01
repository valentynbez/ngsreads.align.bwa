from libc.stdio cimport FILE

cdef extern from "utils.h":
    FILE* err_xopen_core(char func, char fn, char mode)
    long cpu_time()