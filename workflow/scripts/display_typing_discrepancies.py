#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd

parser  = argparse.ArgumentParser()

parser.add_argument("--verification",
                    help="Verification result to find typing discrepancies from",
                    type=Path)
parser.add_argument("--input",
                    help="Reference plasmidfinder typing hashes",
                    type=Path)
parser.add_argument("--ref-input",
                    help="Reference plasmidfinder typing hashes",
                    type=Path)
parser.add_argument("--output",
                    help="Output directory",
                    type=Path)

args = parser.parse_args()


def compare_typing(sample, comparison, ref_input, test_input, output):
    ref_path = ref_input.joinpath(f"{comparison}_data", f"{sample}.tsv")
    test_path = test_input.joinpath(f"{comparison}_data", f"{sample}.tsv")
    df_ref = pd.read_csv(ref_path, sep='\t')
    df_test = pd.read_csv(test_path, sep='\t')
    print(f"df_ref shape: {df_ref.shape}. df_test shape: {df_test.shape}")
    df_comp = df_ref.merge(df_test, indicator=True, how="outer").loc[lambda x: x['_merge']!='both']
    df_comp["Result"] = df_comp["_merge"].map({"left_only": "Reference", "right_only": "Test"})
    df_comp.drop("_merge", axis=1, inplace=True)
    print(f"df_comp shape: {df_comp.shape}")
    output_path = output.joinpath(f"{sample}_{comparison}.tsv")
    df_comp.to_csv(output_path, sep='\t', index=False)

def main(args):
    df = pd.read_csv(args.verification, sep='\t', dtype={'plasmidfinder': str, 'resfinder': str})
    list_discrepant_samples_pf = list(df[df['plasmidfinder'] == "False"]['sample'])
    list_discrepant_samples_rf = list(df[df['resfinder'] == "False"]['sample'])

    Path(args.output).mkdir(parents=True, exist_ok=True)

    print(f"list_discrepant_samples_pf is {list_discrepant_samples_pf}")
    for sample in list_discrepant_samples_pf:
        compare_typing(sample, "plasmidfinder", args.ref_input, args.input, args.output)

    print(f"list_discrepant_samples_rf is {list_discrepant_samples_rf}")
    for sample in list_discrepant_samples_rf:
        compare_typing(sample, "resfinder", args.ref_input, args.input, args.output)

if __name__ == "__main__":
    main(args)