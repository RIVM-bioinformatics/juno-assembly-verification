import pandas as pd
import argparse

def merge_and_compare_tables(files):
    # Read the tables using pandas and merge them based on the first column
    dfs = [pd.read_csv(file, sep='\t') for file in files]
    merged_df = pd.merge(dfs[0], dfs[1], on=dfs[0].columns[0], suffixes=('_file1', '_file2'))
    merged_df = pd.merge(merged_df, dfs[2], on=dfs[0].columns[0])

    # Compare the columns of each table with the merged table
    comparison_results = []
    for i in range(1, len(dfs) + 1):
        comparison_results.append(merged_df.iloc[:, i] == merged_df.iloc[:, -1])

    # Check for discrepancies
    discrepancies = ~(comparison_results[0] & comparison_results[1] & comparison_results[2])
    non_identical_rows = merged_df[discrepancies]

    return discrepancies, non_identical_rows

def save_non_identical_rows(file, non_identical_rows):
    # Save the non-identical rows to a new file
    non_identical_rows.to_csv(file, sep='\t', index=False)

def generate_summary_text(analysis, identical_count, total_samples):
    summary_text = f"For the {analysis} analysis, there were {identical_count} samples for which results were identical, out of a total of {total_samples} samples."
    return summary_text

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge and compare tab-separated tables.')
    parser.add_argument('files', nargs=3, type=str, help='Paths to the three tab-separated files')
    parser.add_argument('--analysis', type=str, required=True, help='Name of the analysis')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output file for discrepancies')
    args = parser.parse_args()

    discrepancies, non_identical_rows = merge_and_compare_tables(args.files)

    if discrepancies.any():
        print("There are discrepancies between the three tables.")
        save_non_identical_rows(args.output_file, non_identical_rows)
        print(f"Discrepancies have been saved to {args.output_file}.")
    else:
        print(f"The second columns of all three tables are identical for the {args.analysis} analysis.")

    total_samples = len(non_identical_rows) + discrepancies.sum()
    summary_text = generate_summary_text(args.analysis, discrepancies.sum(), total_samples)
    print(summary_text)
