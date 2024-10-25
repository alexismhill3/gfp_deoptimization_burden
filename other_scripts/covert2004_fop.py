import numpy as np
import csv
import pandas as pd
import Bio.Entrez
from urllib.error import HTTPError
from defusedxml.ElementTree import parse, tostring
from rich import print
from copy import copy
import json
import re
import statistics

from Bio import Entrez, SeqIO

# Set your email (required for NCBI Entrez usage)
Entrez.email = "email"  # Replace with your actual email
Entrez.api_key = "apikey"

def fetch_cds_by_locus_tag(locus_tag):
    print(locus_tag)
    try:
        # Search NCBI Gene database for the locus tag
        search_handle = Entrez.esearch(db="gene", term=f"{locus_tag}[Gene Name] AND Escherichia coli[Organism]")
        search_results = Entrez.read(search_handle)
        search_handle.close()

        if not search_results["IdList"]:
            #print(f"No gene found for locus tag: {locus_tag}")
            return ""

        gene_id = search_results["IdList"][0]  # Take the first result (most relevant)

        # Fetch gene information
        gene_handle = Entrez.efetch(db="gene", id=gene_id, rettype="gb", retmode="text")
        gene_record = gene_handle.read()
        print(gene_record)

        # Regex pattern to extract the accession, start, and end coordinates
        pattern = r"NC_\d+\.\d+\s*\((\d+)\.\.(\d+)(?:,\s*complement)?\)"

        # Search for the pattern in the text
        match = re.search(pattern, gene_record)

        if match:
            accession = match.group(0).split()[0]  # Accession number
            start = match.group(1)  # Start coordinate
            end = match.group(2)    # End coordinate
            print(f"Accession: {accession}")
            print(f"Start: {start}")
            print(f"End: {end}")
        else:
            print("Pattern not found.")
            return("")


        # Step 2: Fetch the nucleotide sequence using the parsed information
        nuc_handle = Entrez.efetch(db="nuccore", id=accession, rettype="gb", retmode="text", seq_start=start, seq_stop=end)
        nuc_record = SeqIO.read(nuc_handle, "genbank")

        # Step 3: Extract and print the CDS
        for feature in nuc_record.features:
            if feature.type == "CDS":
                cds_seq = feature.extract(nuc_record.seq)  # Extract the sequence
                #print(f"CDS Sequence: {cds_seq}")
                if cds_seq and int(end)-int(start)+1 == len(cds_seq):
                    print(f"Sequence: {cds_seq}")
                    return cds_seq
    except:
        return ""

opt_codons_E_coli = { 'A':['GCT'], 'R':['CGT', 'CGC'], 'N':['AAC'], 'D':['GAC'], 'C':['TGC'], 'Q':['CAG'], 'E':['GAA'], 'G':['GGT','GGC'], 'H':['CAC'], 'I':['ATC'], 'L':['CTG'], 'F':['TTC'], 'P':['CCG'], 'S':['TCT','TCC'], 'T':['ACT','ACC'], 'Y':['TAC'], 'V':['GTT','GTA'] }
reverse_genetic_code = {  'A':['GCA', 'GCC', 'GCG', 'GCT'], 'R':['AGA', 'AGG', 'CGA', 'CGT', 'CGC', 'CGG'], 'N':['AAC', 'AAT'], 'D':['GAC', 'GAT'], 'C':['TGC', 'TGT' ], 'Q':['CAA', 'CAG'], 'E':['GAA', 'GAG'], 'G':['GGA', 'GGC', 'GGG', 'GGT'], 'H':['CAC', 'CAT'], 'I':['ATA', 'ATC', 'ATT'], 'L':['CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG'], 'F':['TTT', 'TTC'], 'P':['CCA', 'CCC', 'CCG', 'CCT'], 'S':['AGC', 'AGT', 'TCA', 'TCC','TCG','TCT'], 'T':[ 'ACA', 'ACT', 'ACC', 'ACG' ], 'Y':['TAC', 'TAT'], 'V':['GTA', 'GTC', 'GTG', 'GTT'], 'W':['TGG'], 'M':['ATG'], 'K':['AAA', 'AAG'], '*':['TAA', 'TAG', 'TGA']}
forward_genetic_code = {}
for key, value in reverse_genetic_code.items():
    for codon in value:
        forward_genetic_code[codon] = key

def calc_Fop( seq, opt_codons = opt_codons_E_coli):
    """Calculates the fraction of optimal codons in a sequence. The fraction is calculated relative to the number of sites where an optimal codon is possible (i.e., for example, methionines are excluded since they are coded by only one amino acid).
"""
    assert len(seq) % 3 == 0

    codon_list = [j for i in opt_codons.values() for j in i]
    aa_list = opt_codons.keys()
    total_count = 0
    opt_count = 0

    for i in range(int(len(seq)/3)):
        codon = seq[3*i:3*i+3]
        aa = forward_genetic_code[codon]
        ignore = True
        opt = False
        if aa in aa_list:
            ignore = False
            c = str( codon )
            opt = (c in codon_list)
        total_count += not ignore
        opt_count += opt

    fopt = float(opt_count/total_count)
    return fopt


def main():
    #df = pd.read_csv("covert2004.csv")
    #df = df[df['Accession'].notna()]
    #gene = fetch_cds_by_locus_tag("b0001")
    #df['cds']=np.where(df.cds=='',df.Accession.map(fetch_cds_by_locus_tag),df.cds).astype(str)

    #df.to_csv("with_seq.csv")
    df = pd.read_csv("with_seq.csv")

    df['avg'] = (df["ec_aer_wild_O_a"] + df["ec_aer_wild_O_b"] + df["ec_aer_wild_O_c"])/3
    df = df[df['cds'].notna()]
    df = df[df.cds.astype(str).str.len() > 0]
    df = df[df.cds.astype(str).str.len() % 3 == 0]
    top_5_per = int(len(df)*0.05)
    df = df.sort_values(by="avg", ascending=False)
    df = df.head(top_5_per)

    df['fop']= df.cds.map(calc_Fop)
    print(df)
    print(statistics.mean(df['fop']))


if __name__ == "__main__":
    main()
