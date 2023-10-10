from bwalib.bwa cimport bwa_idx_build
from bwalib.bntseq cimport bns_fasta2bntseq
from bwalib.utils cimport xzopen
from zlib cimport gzFile

def pack_fasta(filepath, prefix, for_only):
    """
    Creates .pac file of index for reference genome.

    Args:
        filepath (str): Path to reference genome fasta file.
        prefix (str): Prefix of index files.
        for_only (bool): Whether to index only the forward strand.

    Returns:
        None
    """
    cdef gzFile gzip_buffer
    cdef bytes filepath_bytes
    cdef bytes prefix_bytes

    filepath_bytes = filepath.encode("utf-8")
    prefix_bytes = prefix.encode("utf-8")

    # open file
    gzip_buffer = xzopen(filepath_bytes, "r")

    return bns_fasta2bntseq(gzip_buffer, prefix_bytes, for_only)
