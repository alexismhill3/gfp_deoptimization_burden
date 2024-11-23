import sys
from trnasimtools.simulate import SimulateSingleCodonSingleTranscript


simulator = SimulateSingleCodonSingleTranscript(config_file=sys.argv[1],
                                                seed=int(sys.argv[2]),
                                                ribosome_params = (int(sys.argv[6]), 15)
                                                )

simulator.simulate(output_dir=sys.argv[3], time_limit=int(sys.argv[4]), time_step=float(sys.argv[5]))