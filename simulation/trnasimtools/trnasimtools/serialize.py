import yaml
import random
from typing import Dict, Tuple, Optional, List

class SerializeSingleCodonSingleTranscript():

    def __init__(self, 
                 transcript_len: int,  
                 trna_charging_rate: float,
                 ribosome_binding_rate: float,
                 ribosome_copy_number: int,
                 transcript_copy_number: int,
                 total_trna: int,
                 ):
        self.transcript_len = transcript_len
        
        self.params = {}
        self.params["trna_charging_rate"] = trna_charging_rate
        self.params["ribosome_binding_rate"] = ribosome_binding_rate
        self.params["ribosome_copy_number"] = ribosome_copy_number
        self.params["transcript_copy_number"] = transcript_copy_number
        self.params["total_trna"] = total_trna
        
        self.params["config_filename"] = self._format_filename()
        self.params["transcript_data"] = [{}]
        self.params["transcript_data"][0]["transcript_seq"] = self._format_transcript()
        self.params["transcript_data"][0]["transcript_len"] = transcript_len
        self.params["transcript_data"][0]["transcript_name"] = "proteinX"

    def _format_transcript(self):
        codons = ["AAA"] * self.transcript_len
        return "A"*30 + "".join(codons) + "A"*20

    def _format_filename(self):
        base = "single_codon_single_transcript"
        return f"{base}_{self.params['transcript_copy_number']}_{self.params['ribosome_copy_number']}" + \
               f"_{self.params['total_trna']}_{self.params['ribosome_binding_rate']}" + \
               f"_{self.params['trna_charging_rate']}.yaml"
    
    def filename(self):
        return self._format_filename()

    def serialize(self, dir: str):
        with open(f"{dir}/{self._format_filename()}", "w") as stream:
            yaml.dump(self.params, stream)

class SerializeTwoCodonSingleTranscript():

    def __init__(self, 
                 transcript_len: int, 
                 codon_comp: Tuple, 
                 trna_proportion: Tuple, 
                 seed: Optional[int] = 4, 
                 **kwargs):
        self.transcript_len = transcript_len
        self.codon1, self.codon2 = codon_comp
        self.trna1, self.trna2 = trna_proportion
        self.seed = seed
        self.params = kwargs
        self.params["transcript_data"] = [{}]
        self.params["trna_proportion"] = {"TTT": self.trna1, "ATA": self.trna2}
        self.params["config_filename"] = self._format_filename()
        self.params["transcript_data"][0]["transcript_seq"] = self._format_transcript()
        self.params["transcript_data"][0]["transcript_len"] = transcript_len
        self.params["transcript_data"][0]["transcript_name"] = "proteinX"

    def _format_transcript(self):
        codons = ["AAA"] * round(self.transcript_len * self.codon1) + ["TAT"] * round(self.transcript_len * self.codon2)
        random.Random(self.seed).shuffle(codons)
        return "A"*30 + "".join(codons) + "A"*20

    def _format_filename(self):
        base = "two_codon_single_transcript"
        return f"{base}_{self.codon1}_{self.codon2}_{self.trna1}_{self.trna2}.yaml"
    
    def filename(self):
        return self._format_filename()

    def serialize(self, dir: str):
        with open(f"{dir}/{self._format_filename()}", "w") as stream:
            yaml.dump(self.params, stream)


class SerializeTwoCodonMultiTranscript():

    def __init__(self, 
                 transcript_lens: List, 
                 transcript_names: List,
                 codon_comps: List, 
                 trna_proportion: Tuple, 
                 seed: Optional[int] = 4, 
                 **kwargs):
        self.transcript_lens = transcript_lens
        self.codon_comps = codon_comps
        self.trna1, self.trna2 = trna_proportion
        self.seed = seed
        self.params = kwargs
        self.params["transcript_data"] = []
        self.params["trna_proportion"] = {"TTT": self.trna1, "ATA": self.trna2}
        self.params["config_filename"] = self._format_filename()
        for (len, codon_comp, name) in zip(transcript_lens, codon_comps, transcript_names):
            data = {}
            data["transcript_seq"] = self._format_transcript(len, codon_comp)
            data["transcript_len"] = len
            data["transcript_name"] = name
            self.params["transcript_data"].append(data)

    def _format_transcript(self, len, codon_comp):
        codon1, codon2 = codon_comp
        codons = ["AAA"] * round(len * codon1) + ["TAT"] * round(len * codon2)
        random.Random(self.seed).shuffle(codons)
        return "A"*30 + "".join(codons) + "A"*20

    def _format_filename(self):
        base = "two_codon_multi_transcript"
        codon_str = ""
        for codon_comp in self.codon_comps:
            codon_str = codon_str + f"{codon_comp[0]}_{codon_comp[1]}_"
        return f"{base}_{codon_str}{self.trna1}_{self.trna2}.yaml"
    
    def filename(self):
        return self._format_filename()

    def serialize(self, dir: str):
        with open(f"{dir}/{self._format_filename()}", "w") as stream:
            yaml.dump(self.params, stream)
            