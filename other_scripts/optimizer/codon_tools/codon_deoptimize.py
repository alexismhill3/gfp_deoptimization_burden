#!/usr/bin/env python3
import argparse, sys, numbers
from typing import Union

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from codon_tools import CodonOptimizer, FopScorer, opt_codons_E_coli

def deoptimize(
    seq: Union[str, Seq] ,
    gene_description: str,
    Fop_step: float,
    Fop_stop: float,
    start_window:int = 14,
    end_window: int = 14,
    tolerance: float = 0.01,
    max_wait_count: int =10000,
    opt_codons: dict = opt_codons_E_coli,
) -> list[Seq]:
    """Takes a sequence and codon (de)optimizes it to the target Fop_stop
    Keword arguments:
    seq -- Primary DNA sequence to deoptimize. str or Seq object
    gene_description -- Sequence metadata. str
    Fop_step -- how large of a difference to target for each optimization step. float. 0<n<1.
    Fop_stop -- target Fop score. float. 0<=n<=1.
    start_window -- n codons to exclude from optimization. int. default=14
    end_window -- n codons to omit at end of sequence. int. default=14
    * ``opt_codons``: set of optimal codons

    """
    assert len(seq) % 3 == 0
    if not len(seq) % 3 == 0:
        raise ValueError("Sequence length must be divisible by 3 (no partial codons)")
    if not isinstance(Fop_step, float):
        raise ValueError(f"Fop_step must be a float (it is an {type(Fop_step)}")
    if 0 >= Fop_step or Fop_step >= 1:
        raise ValueError(f"Fop step out of range (0<={Fop_step}<=1 fails)")
    if not isinstance(Fop_stop, float) or (isinstance(Fop_stop, numbers.Number) and (Fop_stop == 1 or Fop_stop == 0)):
        raise ValueError(f"Fop_step must be a float, 0, or 1 (it is an {type(Fop_step)}")
    if 0 >= Fop_step or Fop_step >= 1:
        raise ValueError(f"Fop step out of range (0<={Fop_step}<=1 fails)")
    if start_window*3 > len(seq):
        raise ValueError("Entire sequence excluded by start_window")
    if end_window*3 > len(seq):
        raise ValueError("Entire sequence excluded by end_window")
    if start_window*3 + end_window*3 > len(seq):
        raise ValueError("Entire sequence excluded by the sum of start_window and end_window")
    if isinstance(seq, str):
        seq = Seq(seq)

    scorer = FopScorer()
    o = CodonOptimizer(scorer)

    score = scorer.score(seq)
    seq_orig = seq
    Fop_orig = score
    records = [
        SeqRecord(seq, id="", description=gene_description + " -- Fop = %f" % Fop_orig)
    ]
    Fop_start = Fop_orig
    while True:
        if Fop_step < 0:
            Fop_target = Fop_start - tolerance
        else:
            Fop_target = Fop_start + tolerance
        if Fop_target < score:
            maximize = False
            Fop_step = -abs(Fop_step)
        else:
            maximize = True
            Fop_step = abs(Fop_step)
        seq, score = o.hillclimb(
            seq,
            start_window,
            end_window,
            Fop_target,
            tolerance,
            max_wait_count,
            maximize,
            verbosity=0,
        )
        assert seq_orig.translate() == seq.translate()

        description = (
            gene_description
            + " -- recoded to Fop = %f (keeping first %i and last %i codons unchanged)"
            % (score, start_window, end_window)
        )
        seq_record = SeqRecord(seq, id="", description=description)
        setattr(seq_record, "score", score)
        records.append(seq_record)

        Fop_start += Fop_step
        if Fop_step * (Fop_stop - Fop_start) < 0:
            break

    return records


# when run as its own script
if __name__ == "__main__":
    # set up command line arguments
    parser = argparse.ArgumentParser(description="Codon-deoptimize gene sequence.")
    parser.add_argument(
        "filename", metavar="filename", help="fasta-formatted file holding the sequence"
    )
    parser.add_argument(
        "-x",
        "--exclude-front",
        default=14,
        type=int,
        metavar="n",
        help="number of codons to exclude from the front of the sequence, default = 14",
    )
    parser.add_argument(
        "-X",
        "--exclude-back",
        default=14,
        type=int,
        metavar="n",
        help="number of codons to exclude from the back of the sequence, default = 14",
    )
    parser.add_argument(
        "-d",
        "--Fop-step",
        default=-0.1,
        type=float,
        metavar="x",
        help="step size from one Fop value to the next, default = -0.1",
    )
    parser.add_argument(
        "-e",
        "--Fop-stop",
        default=0.1,
        type=float,
        metavar="x",
        help="end value for Fop, default = 0.1",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        default=0.01,
        type=float,
        metavar="t",
        help="Tolerance for final sequence Fop = 0.01",
    )
    parser.add_argument(
        "-M",
        "--max-wait",
        default=5000,
        type=int,
        metavar="n",
        help="maximum number of attempted codon substitutions before we give up the optimization procedure, default = 5000",
    )

    args = parser.parse_args()

    # read in the sequence
    record = SeqIO.parse(open(args.filename, "rU"), "fasta").__next__()
    # run analysis
    records = deoptimize(
        record.seq,
        record.description,
        args.Fop_step,
        args.Fop_stop,
        args.exclude_front,
        args.exclude_back,
        args.tolerance,
        args.max_wait,
    )
    SeqIO.write(records, sys.stdout, "fasta")
