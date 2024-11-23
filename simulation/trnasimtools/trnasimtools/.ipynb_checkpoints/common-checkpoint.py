import pinetree as pt

def add_transcripts(ribosome_params,
                    transcript_data,
                    transcript_copy_number,
                    ribosome_binding_rate,
                    model, 
                    name = "proteinX"):
    ribosome_footprint = ribosome_params[1]
    # convert CDS length to nt and add 50 nt buffer (30 upstream, 20 downstream)
    transcript_len = transcript_data["transcript_len"] * 3 + 50
    i = 0
    # pinetree can only add one transcript at a time for some reason, so do this in a loop
    while i < transcript_copy_number:
        transcript = pt.Transcript("transcript", transcript_len)
        transcript.add_gene(name=transcript_data["transcript_name"], start=31, stop=transcript_len - 20,
                            rbs_start=(31 - ribosome_footprint), rbs_stop=31, 
                            rbs_strength=ribosome_binding_rate)
        transcript.add_seq(seq=transcript_data["transcript_seq"])
        model.register_transcript(transcript)
        i += 1

def add_two_trna_species(simulation_data,
                         total_trna,
                         trna_charging_rates,
                         model):
    trna1_proportion = simulation_data["trna_proportion"]["TTT"]
    trna2_proportion = simulation_data["trna_proportion"]["ATA"]
    counts_map = {"TTT": [int(total_trna * trna1_proportion), 0], 
                    "ATA": [int(total_trna * trna2_proportion), 0]}
    trna_map = {"AAA": ["TTT"], "TAT": ["ATA"]}
    rates_map = {"TTT": trna_charging_rates[0], "ATA": trna_charging_rates[1]}
    model.add_trna(trna_map, counts_map, rates_map)
