import os
import unittest
from io import StringIO
import tempfile


from ngsreads.align.bwa import pack_fasta

class TestIndex(unittest.TestCase):

    # def test_index(self):

    #     mock_fasta = "tests/data/test.fa"
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         # prefix = os.path.join(tmpdir, "idx")
    #         prefix = "idx"
    #         index_build(mock_fasta, prefix, 0, 10000000)
    #         prefix_files = [prefix + x for x in [".amb", ".ann", ".bwt", ".pac", ".sa"]]
    #         for f in prefix_files:
    #             self.assertTrue(os.path.isfile(f))

    def test_packing(self):

        mock_fasta = "tests/data/test.fa"
        prefix = "pack"
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix = os.path.join(tmpdir, prefix)
            pack_fasta(mock_fasta, prefix, 0)
            suffixes = [".pac", ".amb", ".ann"]
            for s in suffixes:
                self.assertTrue(os.path.isfile(prefix + s))


