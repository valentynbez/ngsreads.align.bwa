# Expose zlib to Cython

from libc.stdint cimport int64_t

cdef extern from "zlib.h" nogil:
    ctypedef void *gzFile
    ctypedef int64_t z_off_t

    cdef int gzclose(gzFile fp)
    cdef gzFile gzopen(char *path, char *mode)