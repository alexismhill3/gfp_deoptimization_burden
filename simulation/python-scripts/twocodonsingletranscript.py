import sys
from trnasimtools.simulate import SimulateTwoCodonSingleTranscript


simulator = SimulateTwoCodonSingleTranscript(config_file=sys.argv[1],
                                             seed=int(sys.argv[2]),
                                             transcript_copy_number=int(sys.argv[3]),
                                             ribosome_copy_number=int(sys.argv[4]),
                                             total_trna=int(sys.argv[5]),
                                             ribosome_binding_rate=float(sys.argv[6]),
                                             trna_charging_rates=[float(sys.argv[7]), float(sys.argv[8])])
simulator.simulate(sys.argv[9])
