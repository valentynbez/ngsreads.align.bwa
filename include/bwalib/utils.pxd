from zlib cimport gzFile
from libc.stdio cimport FILE

cdef extern from "utils.h" nogil:
    cdef gzFile xzopen(char *filename, char *mode)
