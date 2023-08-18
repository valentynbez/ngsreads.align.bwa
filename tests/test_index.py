import unittest
from ngsreads.align.bwa import bwa_idx_build

class TestIndex(unittest.TestCase):
    def SetUp(self):
        # simulate gzipped fasta
        self.fasta = "tests/test.fa"

    def test_index_build(self):
        bwa_idx_build(self.fasta, "idx", 0, 10000000)

