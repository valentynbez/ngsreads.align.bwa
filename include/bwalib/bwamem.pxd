cdef extern from "bwamem.h" nogil:
    cdef enum MEM_F:
        MEM_F_PE=2
        MEM_F_NOPAIRING=4
        MEM_F_ALL=8
        MEM_F_NO_MULTI=10
        MEM_F_NO_RESCUE=20
        MEM_F_REF_HDR=100
        MEM_F_SOFTCLIP=200
        MEM_F_SMARTPE=400
        MEM_F_PRIMARY5=800
        MEM_F_KEEP_SUPP_MAPQ=1000
        MEM_F_XB = 2000

    cdef struct mem_opt_t:
        int match_score
        int missmatch_penalty
        int o_del
        int e_del
        int o_ins
        int e_ins
        int pen_unpaired       # phred-scaled penalty for unpaired reads
        int pen_clip5          # clipping penalty for 5'-end
        int pen_clip3          # clipping penalty for 3'-end
        int w                  # bandwidth
        int zdrop              # Z-dropoff

        int max_mem_intv

        int T                  # minimum score to output
        int flag
        int min_seed_len
        int min_chain_weight
        int max_chain_extend
        int split_factor       # split into a seed if MEM is longer than min_seed_len*split_factor
        int split_width        # split into a seed if its occurence is smaller than this value
        int max_occ            # skip a seed if its occurence is larger than this value
        int max_chain_gap      # do not chain seed if it is max_chain_gap-bp away from the closest seed
        int n_threads
        int chunk_size         # process chunk_size-bp sequences in a batch
        float mask_level       # regard a hit as redundant if the overlap with another better
                               # hit is over mask_level times the min length of the two hits
        float drop_ratio       # drop a chain if its seed coverage is below drop_ratio times
                               # the seed coverage of a better chain overlapping with the small chain
        float XA_drop_ratio    # when counting hits for the XA tag, ignore alignments with score < XA_drop_ratio * max_score;
                               # only effective for the XA tag
        float mask_level_redun
        float mapQ_coef_len
        int mapQ_coef_fac
        int max_ins           # when estimating insert size distribution, skip pairs with insert longer than this value
        int max_XA_hits       # perform maximally max_matesw rounds of mate-SW for each end
        int max_XA_hits_alt   # if there are max_hits or fewer, output them all
        int mat[25]           # scoring matrix; mat[0] is used if unset

    cdef struct mem_pestat_t:
        int low     # lower bound within which a read pair is properly paired
        int high    # upper bound within which a read pair is properly paired
        int failed  # non-zero if the orientation is not supported by data
        float avg   # average insert size
        float std   # standard deviation of insert size

    cdef struct mem_alnreg_t
        int rb              #  [rb,re): reference sequence in the alignment
        int re
        int qb              #  [qb,qe): query sequence in the alignment
        int qe
        int rid             # refrerence seq ID
        int score           # best local SW score
        int truesc          # actual score corresponding to the aligned region, possibly smaller than # score
        int sub             # 2nd best SW score
        int alt_sc
        int csub            # SW score of a tandem hit
        int sub_n           # number of suboptimal hits
        int w               # actual band width used in extension
        int seedcov         # length of regions covered by seeds
        int secondary       # index of the parent hit shadowing the current hit; <0 if primary
        int secondary_all
        int seedlen0        # length of the starting seed
        int n_comp          # number of sub-alignments chained together
        int is_alt
        int hash

    # This struct is only used for the convenience of API.
    cdef struct mem_aln_t:
        int pos             # forward strand 5'-end mapping position
        int rid             # reference sequence index in bntseq_t; <0 for unmapped
        int flag            # extra flag
        int is_rev          # whether on the reverse strand
        int is_alt          # whether this alignment is an alternative alignment
        int mapQ_coef_fac   # mapping quality
        int NM              # edit distance
        int n_cigar         # number of CIGAR operations
        int *cigar          # CIGAR in the BAM encoding: opLen<<4|op; op to integer mapping: MIDSH=>01234
        char *XA            # alternative mappings
        int score
        int sub
        int alt_sc