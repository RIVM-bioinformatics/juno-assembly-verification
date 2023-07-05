#!/usr/bin/env python3

import pandas as pd
import pathlib
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input",
                    type=pathlib.Path,
                    help="Input file to select columns from",
                    metavar="FILE")
parser.add_argument("-o", "--output",
                    type=pathlib.Path,
                    help="Output table",
                    metavar="FILE")
parser.add_argument("-c", "--columns",
                    type=str,
                    metavar="STR")

args = parser.parse_args()

list_relevant_columns = args.columns.split(',')

# Read df, subset relevant columns and sort by these columns
df = pd.read_csv(args.input, dtype='str', sep='\t')
df_selection = df[list_relevant_columns]
df_selection_sorted = df_selection.sort_values(list_relevant_columns)

df_selection_sorted.to_csv(args.output, sep='\t', index=False)