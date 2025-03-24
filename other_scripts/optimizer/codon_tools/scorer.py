from .sequence_analyzer import SequenceAnalyzer
from .lookup_tables import opt_codons_E_coli

class FopScorer:
    """Scores sequences based on the fraction of optimal codons. By default, uses the E. coli optimal codons from Zhou et al. 2009. A different set of optimal codons can be specified in the constructor."""

    def __init__(self, opt_codons=opt_codons_E_coli):
        self.sa = SequenceAnalyzer()
        self.opt_codons = opt_codons

    def score(self, seq):
        opt_count, total_count, Fop = self.sa.calc_Fop(seq, self.opt_codons)
        return Fop
