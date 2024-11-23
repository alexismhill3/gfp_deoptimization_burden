import pytest
import tempfile
import shutil
import filecmp
import pinetree as pt
import yaml
from trnasimtools.serialize import SerializeTwoCodonMultiTranscript
from trnasimtools.simulate import SimulateTwoCodonMultiTranscript

RB_COPY = 100
TS_COPY = [100, 100]
RBS_STRENGTH = [10000.0, 5000.0]
TRNA_CHRG_RATES = [100.0, 100.0]
TRNA_PROPORTIONS = (0.9, 0.1)
TOTAL_TRNA = 100
TIME_LIMIT = 50
TIME_STEP = 5
SEED = 1

def sim_hardcoded_multi_transcript(dir):
    seq_9_1 = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAATATTATTATTATAAATATTATTATTATTATTATTATAAATATTATTATTATTATTATTATTATTATAAATATAAATATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATAAATATTATTATTATTATAAATATTATTATTATTATTATTATTATTATTATTATTATTATTATTATTATAAATATTATTATTATTATTATTATTATTATAAATATTATTATAAAAAATATTATTATTATTATTATTATTATAAAAAAAAAAAAAAAAAAAA"

    seq_6_4 = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAATATTATTATAAAAAATATTATTATTATTATAAATATAAATATTATTATTATTATTATTATTATTATAAATATAAATATTATTATAAATATTATTATAAATATTATTATAAATATAAAAAATATTATTATTATTATAAAAAAAAATATTATTATAAAAAAAAATATTATTATTATTATAAAAAATATAAATATAAATATTATTATTATTATTATAAAAAAAAAAAATATAAAAAAAAATATAAAAAATATTATTATAAAAAAAAATATTATAAAAAAAAAAAATATTATTATAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(SEED)
    sim.add_ribosome(copy_number=RB_COPY, speed=1, footprint=15)
    
    i = 0
    while i < TS_COPY[0]:
        transcript = pt.Transcript("transcript", 350)
        transcript.add_gene(name="proteinX", start=31, stop=330,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=RBS_STRENGTH[0])
        transcript.add_seq(seq=seq_9_1)
        sim.register_transcript(transcript)
        i += 1

    i = 0
    while i < TS_COPY[1]:
        transcript = pt.Transcript("transcript", 350)
        transcript.add_gene(name="proteinY", start=31, stop=330,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=RBS_STRENGTH[1])
        transcript.add_seq(seq=seq_6_4)
        sim.register_transcript(transcript)
        i += 1

    tRNA_map = {"AAA": ["TTT"], "TAT": ["ATA"]}
    tRNA_counts = {"TTT": [int(TOTAL_TRNA*TRNA_PROPORTIONS[0]), 0], "ATA": [int(TOTAL_TRNA*TRNA_PROPORTIONS[1]), 0]}
    tRNA_rates = {"TTT": TRNA_CHRG_RATES[0], "ATA": TRNA_CHRG_RATES[1]}
    sim.add_trna(tRNA_map, tRNA_counts, tRNA_rates)
    output = "sim_hardcoded.tsv"
    sim.simulate(time_limit=TIME_LIMIT, time_step=TIME_STEP, output=f"{dir}/{output}")
    return output

def sim_using_classes_multi_transcript(dir):
    serializer = SerializeTwoCodonMultiTranscript(transcript_lens=[100, 100],
                                                   codon_comps=[(0.1, 0.9), (0.4, 0.6)],
                                                   transcript_names=["proteinX", "proteinY"],
                                                   trna_proportion=TRNA_PROPORTIONS,
                                                   transcript_copy_numbers=TS_COPY,
                                                   ribosome_binding_rates=RBS_STRENGTH,
                                                   ribosome_copy_number=RB_COPY,
                                                   total_trna=TOTAL_TRNA,
                                                   trna_charging_rates=TRNA_CHRG_RATES,
                                                   time_limit=TIME_LIMIT,
                                                   time_step=TIME_STEP)
    serializer.serialize(dir)
    config = serializer.filename()

    simulator = SimulateTwoCodonMultiTranscript(config_file=f"{dir}/{config}",
                                                 seed=SEED)
    simulator.simulate(dir)
    return simulator.filename()

def test_twocodonmultitranscript():
    """
    Runs two identical simulations, with and without the TwoCodonSingleTranscript
    wrapper/helper classes, and checks that the output from each is the same (it should be). 
    """
    tmpdir = tempfile.mkdtemp()
    output1 = sim_hardcoded_multi_transcript(tmpdir)
    output2 = sim_using_classes_multi_transcript(tmpdir)
    assert filecmp.cmp(f"{tmpdir}/{output1}", f"{tmpdir}/{output2}")
    shutil.rmtree(tmpdir)
