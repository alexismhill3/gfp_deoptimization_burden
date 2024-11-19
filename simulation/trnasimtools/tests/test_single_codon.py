import pytest
import tempfile
import shutil
import filecmp
import pinetree as pt
import yaml
from trnasimtools.serialize import SerializeSingleCodonSingleTranscript
from trnasimtools.simulate import SimulateSingleCodonSingleTranscript

RB_COPY = 100
TS_COPY = 100
RBS_STRENGTH = 10000.0
TRNA_CHRG_RATE = 100.0
TOTAL_TRNA = 100
TIME_LIMIT = 50
TIME_STEP = 5
SEED = 1

def sim_hardcoded(dir):
    seq = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    sim = pt.Model(cell_volume=8e-16)
    sim.seed(SEED)
    sim.add_ribosome(copy_number=RB_COPY, speed=1, footprint=15)
    
    i = 0
    while i < TS_COPY:
        transcript = pt.Transcript("transcript", 350)
        transcript.add_gene(name="proteinX", start=31, stop=330,
                     rbs_start=(31 - 15), rbs_stop=31, rbs_strength=RBS_STRENGTH)
        transcript.add_seq(seq=seq)
        sim.register_transcript(transcript)
        i += 1

    tRNA_map = {"AAA": {"TTT": {"charged": TOTAL_TRNA, "uncharged": 0}},}
    sim.add_trna(tRNA_map, TRNA_CHRG_RATE)
    output = "sim_hardcoded.tsv"
    sim.simulate(time_limit=TIME_LIMIT, time_step=TIME_STEP, output=f"{dir}/{output}")
    return output

def sim_using_classes(dir):
    serializer = SerializeSingleCodonSingleTranscript(transcript_len=100,
                                                   transcript_copy_number=TS_COPY,
                                                   ribosome_binding_rate=RBS_STRENGTH,
                                                   ribosome_copy_number=RB_COPY,
                                                   total_trna=TOTAL_TRNA,
                                                   trna_charging_rate=TRNA_CHRG_RATE
                                                   )
    serializer.serialize(dir)
    config = serializer.filename()

    simulator = SimulateSingleCodonSingleTranscript(config_file=f"{dir}/{config}",
                                                 seed=SEED)
    simulator.simulate(output_dir=dir, time_limit=TIME_LIMIT, time_step=TIME_STEP)
    return simulator.filename()

def test_singlecodonsingletranscript():
    """
    Runs two identical simulations, with and without the TwoCodonSingleTranscript
    wrapper/helper classes, and checks that the output from each is the same (it should be). 
    """
    #sim_using_classes(".")
    tmpdir = tempfile.mkdtemp()
    output1 = sim_hardcoded(tmpdir)
    output2 = sim_using_classes(tmpdir)
    assert filecmp.cmp(f"{tmpdir}/{output1}", f"{tmpdir}/{output2}")
    shutil.rmtree(tmpdir)


