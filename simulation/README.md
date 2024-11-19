This folder contains all notebooks, python scripts, and software dependencies that were used to run simulations in Roots et al 2024:

- `*.ipynb` Creates config files and generates batch scripts for a set of simulations.
- `scripts` Sets up and executes a single Pinetree simulation with tRNA dyanmics.
- `trnasimtools` Mini python package with common functions for running tRNA dyanmics simulations with Pinetree.
- `pinetree-dyanmic-trnas` Modified version of [Pinetree](https://github.com/clauswilke/pinetree) with dynamic tRNA charging.

Raw simulation outputs are too big to host on github but can be provided upon request. To re-make the manuscript figures from processed/checkpoint data (*.csv) just run the R notebooks `plotting/modeling_figures.Rmd` and `plotting/modeling_supplement.Rmd`. It is also possible to re-run some or all of the simulations from scratch. Note that this will probably require an HPC environment (it took us 2-5 days to finish each batch of simulations running continuously on a 50 CPU machine):

1. Install python dependencies: `pip install -r requirements.txt`
2. Pip install `trnasimtools` and the `Pinetree` fork (cd into each folder and run `pip install .`)
3. Run each notebook up until "Read in simulation output" and run the batch file (`<date>.txt`)
4. Once the simulations have finished, run the rest of the notebook to process outputs into a single dataframe
