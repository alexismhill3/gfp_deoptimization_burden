# Codon Tools

A python package containing various tools for codon optimization and de-optimization. Slightly modified from clauswilke/codon_tools.

This portion of the repo is MIT licensed.

Installation:

* Clone this repo
* `pip install ./` this repo
* `pip install biopython`

Example python usage:
```
from codon_tools import deoptimize
seq = "ATGAGCAAAGGTGAAGAACTGTTTACCGGC..." # Abbreviated
results = deoptimize(
    seq = seq,
    gene_description = "gfp",
    Fop_step = -0.01,
    Fop_stop = 0.15,
    start_window = 15,
    end_window = 0
)
final_result = results[-1]
```

The script will try to reach the target optimization by decreasing the Fraction of Optimal Codons (FOP) if the FOP of the input `seq` FOP is above the target or increasing the FOP if the `seq` FOP is below the target.
