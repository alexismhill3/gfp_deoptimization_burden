import yaml
from typing import Optional, Tuple, List
import pinetree as pt
from trnasimtools.common import add_transcripts, add_two_trna_species

class SimulateSingleCodonSingleTranscript():

    def __init__(self, 
                config_file: str, 
                seed: int,
                ribosome_params: Optional[Tuple] = (1, 15), # speed, footprint
                cell_volume: Optional[float] = 8e-16
                ):
        self.sim_data = self._load_config(config_file)
        self.seed = seed
        self.ribosome_params = ribosome_params
        self.model = pt.Model(cell_volume=cell_volume)

    def _load_config(self, config_file):
        with open(config_file, "r") as stream:
            data = yaml.safe_load(stream)
        return data

    def _add_transcripts(self):
        add_transcripts(self.ribosome_params,
                        self.sim_data["transcript_data"][0],
                        self.sim_data["transcript_copy_number"],
                        self.sim_data["ribosome_binding_rate"],
                        self.model)
    
    def _add_trna(self):
        tRNA = {"AAA": {"TTT": {"charged": self.sim_data["total_trna"], "uncharged": 0}},}
        self.model.add_trna(tRNA, self.sim_data["trna_charging_rate"])
    
    def _add_ribosomes(self):
        speed, footprint = self.ribosome_params
        self.model.add_ribosome(copy_number=self.sim_data["ribosome_copy_number"], speed=speed, footprint=footprint)
    
    def _format_filename(self):
        base = self.sim_data["config_filename"].split(".yaml")[0]
        return f"{base}_{self.seed}.tsv"
    
    def filename(self):
        return self._format_filename()

    def simulate(self, output_dir: str, time_limit: int, time_step: float):
        self.model.seed(self.seed)
        self._add_transcripts()
        self._add_trna()
        self._add_ribosomes()
        outfile = self._format_filename()
        self.model.simulate(time_limit=time_limit, time_step=time_step, output=f"{output_dir}/{outfile}")

        
class SimulateTwoCodonSingleTranscript():

    def __init__(self, 
                config_file: str, 
                seed: int,
                trna_charging_rates: Optional[List] = None,
                ribosome_binding_rate: Optional[float] = None,
                ribosome_copy_number: Optional[int] = None,
                transcript_copy_number: Optional[int] = None,
                total_trna: Optional[int] = None,
                ribosome_params: Optional[Tuple] = (1, 15), # speed, footprint
                cell_volume: Optional[float] = 8e-16,
                ):
        self.simulation_data = self._load_config(config_file)
        self.seed = seed
        self.ribosome_params = ribosome_params
        self.model = pt.Model(cell_volume=cell_volume)
        
        self.transcript_copy_number = transcript_copy_number if transcript_copy_number \
                                 is not None else self.simulation_data["transcript_copy_number"]
        self.ribosome_binding_rate = ribosome_binding_rate if ribosome_binding_rate \
                                 is not None else self.simulation_data["ribosome_binding_rate"]
        self.total_trna = total_trna if total_trna \
                                 is not None else self.simulation_data["total_trna"]
        self.trna_charging_rates = trna_charging_rates if trna_charging_rates \
                                 is not None else self.simulation_data["trna_charging_rates"]
        self.ribosome_copy_number = ribosome_copy_number if ribosome_copy_number \
                                 is not None else self.simulation_data["ribosome_copy_number"]

    def _load_config(self, config_file):
        with open(config_file, "r") as stream:
            data = yaml.safe_load(stream)
        return data

    def _add_transcripts(self):
        add_transcripts(self.ribosome_params,
                        self.simulation_data["transcript_data"][0],
                        self.transcript_copy_number,
                        self.ribosome_binding_rate,
                        self.model)
    
    def _add_trna(self):
        add_two_trna_species(self.simulation_data,
                             self.total_trna,
                             self.trna_charging_rates,
                             self.model)
    
    def _add_ribosomes(self):
        speed, footprint = self.ribosome_params
        self.model.add_ribosome(copy_number=self.ribosome_copy_number, speed=speed, footprint=footprint)
    
    def _format_filename(self):
        base = self.simulation_data["config_filename"].split(".yaml")[0]
        return f"{base}_{self.transcript_copy_number}_{self.ribosome_copy_number}_{self.total_trna}_" + \
               f"{self.ribosome_binding_rate}_{self.trna_charging_rates[0]}_{self.trna_charging_rates[0]}_{self.seed}.tsv"
    
    def filename(self):
        return self._format_filename()

    def simulate(self, output_dir: str, time_limit: Optional[int] = None, time_step: Optional[float] = None):
        if time_limit is None:
            time_limit = self.simulation_data["time_limit"]
        if time_step is None:
            time_step = self.simulation_data["time_step"]
        self.model.seed(self.seed)
        self._add_transcripts()
        self._add_trna()
        self._add_ribosomes()
        outfile = self._format_filename()
        self.model.simulate(time_limit=time_limit, time_step=time_step, output=f"{output_dir}/{outfile}")


class SimulateTwoCodonMultiTranscript():

    def __init__(self, 
                config_file: str, 
                seed: int,
                trna_charging_rates: Optional[List] = None,
                ribosome_binding_rates: Optional[List] = None,
                transcript_copy_numbers: Optional[List] = None,
                ribosome_copy_number: Optional[int] = None,
                total_trna: Optional[int] = None,
                ribosome_params: Optional[Tuple] = (1, 15), # speed, footprint
                cell_volume: Optional[float] = 8e-16,
                ):
        self.simulation_data = self._load_config(config_file)
        self.seed = seed
        self.ribosome_params = ribosome_params
        self.model = pt.Model(cell_volume=cell_volume)
        
        self.transcript_copy_numbers = transcript_copy_numbers if transcript_copy_numbers \
                                 is not None else self.simulation_data["transcript_copy_numbers"]
        self.ribosome_binding_rates = ribosome_binding_rates if ribosome_binding_rates \
                                 is not None else self.simulation_data["ribosome_binding_rates"]
        self.total_trna = total_trna if total_trna \
                                 is not None else self.simulation_data["total_trna"]
        self.trna_charging_rates = trna_charging_rates if trna_charging_rates \
                                 is not None else self.simulation_data["trna_charging_rates"]
        self.ribosome_copy_number = ribosome_copy_number if ribosome_copy_number \
                                 is not None else self.simulation_data["ribosome_copy_number"]

    def _load_config(self, config_file):
        with open(config_file, "r") as stream:
            data = yaml.safe_load(stream)
        return data

    def _add_transcripts(self):
        for (transcript_cn, rbs, transcript_data) in \
        zip(self.transcript_copy_numbers, self.ribosome_binding_rates, self.simulation_data["transcript_data"]):
            add_transcripts(self.ribosome_params,
                            transcript_data,
                            transcript_cn,
                            rbs,
                            self.model)
    
    def _add_trna(self):
        add_two_trna_species(self.simulation_data,
                             self.total_trna,
                             self.trna_charging_rates,
                             self.model)
    
    def _add_ribosomes(self):
        speed, footprint = self.ribosome_params
        self.model.add_ribosome(footprint=footprint, speed=speed, copy_number=self.ribosome_copy_number)
    
    def _format_filename(self):
        base = self.simulation_data["config_filename"].split(".yaml")[0]
        transcript_str, rbs_str = ("", "")
        for (transcript_cn, rbs) in zip(self.transcript_copy_numbers, self.ribosome_binding_rates):
            transcript_str = transcript_str + f"{transcript_cn}_"
            rbs_str = rbs_str + f"{rbs}_"
        return f"{base}_{transcript_str}{self.ribosome_copy_number}_{self.total_trna}_" + \
               f"{rbs_str}{self.trna_charging_rates[0]}_{self.trna_charging_rates[0]}_{self.seed}.tsv"
    
    def filename(self):
        return self._format_filename()

    def simulate(self, output_dir: str, time_limit: Optional[int] = None, time_step: Optional[float] = None):
        if time_limit is None:
            time_limit = self.simulation_data["time_limit"]
        if time_step is None:
            time_step = self.simulation_data["time_step"]
        self.model.seed(self.seed)
        self._add_transcripts()
        self._add_trna()
        self._add_ribosomes()
        outfile = self._format_filename()
        self.model.simulate(time_limit=time_limit, time_step=time_step, output=f"{output_dir}/{outfile}")
