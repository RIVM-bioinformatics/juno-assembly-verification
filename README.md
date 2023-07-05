# Juno-assembly verification

This pipeline aims to make the verification of Juno-assembly versions easier.

Validations and verification are organised around pipeline functionalities, which are managed by different groups. Each group has their own criteria for validation and verification. This workflow is organised around this concept: each group has their own verification workflow which is are separate from each other.

Configuration files and reference data are stored in /mnt/db/juno and are under version control of a local (not uploaded) git.

## General components for verification workflows

General components used by workflows

- `config/config_GROUP.tsv`: Config file indicating which columns should be compare with which operator. E.g. "# contigs" from results file (`result_col`) should be less than or equal to (`operator`) 150 contigs for sample X (`criterium_col`). Thresholds/values per sample are defined in `config/verification_criteria_GROUP.tsv`. 
- `config/verification_criteria_GROUP.tsv`: defines per sample which thresholds/values the results should be compared to. `criterium_col` from `config/config_GROUP.tsv` should be present in this file.
- `rules/GROUP/verify_qc.smk`: Snakemake rule which calls `workflow/scripts/verify_qc.py`. The Python script uses `config/config_GROUP.tsv`, `config/verification_criteria_GROUP.tsv` and result files and compares these to assign TRUE/FALSE indicating whether a threshold/value was met. TO DO: separate parsing/summarising of results and actual comparison, this now happens in a single script.

Specific components used

- The AMR workflow also compares typing results. Plasmidfinder and Resfinder containers (including fixed database versions) are used to type assemblies. Relevant data (gene name, nucleotide identity, reference coverage and accession number) are written to a sorted table of which hashes are compared with reference hashes. A hash of the raw output file is not used, as the table order can differ as well positions of hits within an assembly.
- The AMR workflow also outputs a folder `de_novo_assembly_filtered` with assemblies renamed to reflect the Juno-assembly version in the file name. This folder can be used by an automated SeqSphere script to type assemblies according to MLST and wgMLST.


## Contribution guidelines
This pipeline is based on Juno-template.

Juno pipelines use a [feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow). To work on features, create a branch from the `main` branch to make changes to. This branch can be merged to the main branch via a pull request. Hotfixes for bugs can be committed to the `main` branch.

Please adhere to the [conventional commits](https://www.conventionalcommits.org/) specification for commit messages. These commit messages can be picked up by [release please](https://github.com/googleapis/release-please) to create meaningful release messages.
