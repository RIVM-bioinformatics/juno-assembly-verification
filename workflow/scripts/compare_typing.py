#!/usr/bin/env python3

import pandas as pd
import pathlib
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-pf", "--plasmidfinder",
                    type=pathlib.Path,
                    help="Input file with sha256 hashes of all plasmidfinder data",
                    metavar="FILE")
parser.add_argument("-rf", "--resfinder",
                    type=pathlib.Path,
                    help="Input file with sha256 hashes of all resfinder data",
                    metavar="FILE")
parser.add_argument("-o", "--output",
                    type=pathlib.Path,
                    help="Output table",
                    metavar="FILE")

args = parser.parse_args()

def read_df(input_path : pathlib.Path, col_name : str) -> pd.DataFrame:
    """
    Read table of hashes per file.

    Args:
        input_path: path to table with all hashes.
        col_name: intended name for column in output, containing hashed results.
    
    Returns:
        Pandas DataFrame with sample name and hash string.
    """
    df = pd.read_csv(input_path, delim_whitespace=True,
                     header=None, names=[col_name, "file"])
    df['sample'] = df['file'].apply(lambda x: pathlib.Path(x).stem)
    df = df[['sample', col_name]]
    return df

df_pf = read_df(args.plasmidfinder, "plasmidfinder_result")
df_rf = read_df(args.resfinder, "resfinder_result")
df = df_pf.merge(df_rf, on="sample")
df.to_csv(args.output, sep='\t', index=False)
