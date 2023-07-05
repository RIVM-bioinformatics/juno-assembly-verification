import pandas as pd
import openpyxl
import pathlib

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-V", "--verification",
                    help=" Verification criteria per sample",
                    type=pathlib.Path,
                    required=True)
parser.add_argument("-qc", "--qc-report",
                    help=" Juno-assembly QC_report.xlsx",
                    type=pathlib.Path)
parser.add_argument("--quast",
                    help=" Juno-assembly quast transposed_report.tsv",
                    type=pathlib.Path)
parser.add_argument("--bbtools",
                    help=" Juno-assembly bbtools multireport",
                    type=pathlib.Path)
parser.add_argument("--typing-report",
                    help="Typing report to include",
                    type=pathlib.Path)
parser.add_argument("--config",
                    help="Table describing comparisons to make",
                    type=pathlib.Path,
                    required=True)
parser.add_argument("-o", "--output",
                    help="Output verification result",
                    type=pathlib.Path,
                    default="verification_result.tsv")

args = parser.parse_args()

def compare_criterium(result_col : str, operator : str, criterium_col : str, dataframe : pd.DataFrame) -> pd.Series:
    """
    Compare columns from dataframe using specified operator.

    Args:
        result_col: column describing result values.
        operator: comparison to make between result_col and criterium_col.
        criterium_col: column describing threshold or reference value.
        dataframe: dataframe to use for comparisons.
    
    Returns:
        pd.Series of comparisons, expressed as boolean.

    Raises:
        ValueError: if operator is not one of ">", ">=", "<", "<=", "==".
    """
    if operator == ">":
        return dataframe[result_col] > dataframe[criterium_col]
    if operator == ">=":
        return dataframe[result_col] >= dataframe[criterium_col]
    if operator == "<":
        return dataframe[result_col] < dataframe[criterium_col]
    if operator == "<=":
        return dataframe[result_col] <= dataframe[criterium_col]
    elif operator == "==":
        return dataframe[result_col] == dataframe[criterium_col]
    else:
        raise ValueError("Did not recognise operator")

def read_verification_df(path_to_verification : pathlib.Path) -> pd.DataFrame:
    """
    Read in verification table.

    Args:
        path_to_verification: path to verification table.

    Returns:
        Dataframe with verification criteria.
    """
    df_verification = pd.read_csv(path_to_verification, sep='\t')
    df_verification['sample'] = df_verification['sample'].astype(str)
    return df_verification

def use_qc_report(path_qc_report : pathlib.Path, df_verification : pd.DataFrame) -> pd.DataFrame:
    """
    Read QC report and merge with verification table.

    Args:
        path_qc_report: path to QC_report.xlsx from Juno-assembly (v2.1.0 and later).
        df_verification: dataframe with verification criteria.
    
    Returns:
        dataframe with QC report and verification data.
    """
    dict_qc_report = pd.read_excel(path_qc_report, None)
    df_results = pd.concat(dict_qc_report.values())
    df_results['sample'] = df_results['sample'].astype(str)
    df_merged = df_verification.merge(df_results, on="sample")
    return df_merged

def use_quast_and_bbtools(path_quast : pathlib.Path, path_bbtools : pathlib.Path, df_verification : pd.DataFrame) -> pd.DataFrame:
    """
    Read Quast and bbtools summaries and merge with verification table.

    Args:
        path_quast: path to Quast transposed_report.tsv from Juno-assembly.
        path_bbtools: path to bbtools summary_report.tsv from Juno-assembly.
        df_verification: dataframe with verification criteria.
    
    Returns:
        dataframe with Quast, bbtools and verification data.
    """
    df_quast = pd.read_csv(path_quast, sep='\t')
    df_bbtools = pd.read_csv(path_bbtools, sep='\t')
    df_verification['sample_truncated'] = df_verification['sample'].apply(lambda x: str(x).split('_')[0])
    df_out = df_verification.merge(df_quast[['Assembly', '# contigs']], left_on="sample", right_on="Assembly")
    df_out = df_out.merge(df_bbtools[['Sample', 'Average coverage']], left_on="sample_truncated", right_on="Sample")
    return df_out

def add_typing_report(df_results : pd.DataFrame, path_to_typing : pathlib.Path) -> pd.DataFrame:
    """
    Read typing results and merge with verification data.

    Args:
        df_results: dataframe with verification data (can include other data).
        path_to_typing: path to typing report (e.g. result hashes).
    
    Returns:
        dataframe with typing data added.
    """
    df_typing = pd.read_csv(path_to_typing, sep='\t')
    df_results = df_results.merge(df_typing, on="sample")
    return df_results

def compare_to_criteria(df_results : pd.DataFrame, path_to_config : pathlib.Path) -> pd.DataFrame:
    """
    Compare results with verification thresholds/reference values.

    Args:
        df_results: dataframe with all results and verification data needed for comparisons.
        path_to_config: path to config table, outlining which comparisons to make.
    
    Returns:
        dataframe with only the comparisons specified in path_to_config.
    """
    df_config = pd.read_csv(path_to_config, sep="\t")

    df_output = df_results[['sample', 'organism']].copy()

    # Compare columns in df_results by looping over df_config lines
    for index, row in df_config.iterrows():
        comp_name = row['comparison_name']
        operator_name = '_'.join(["operator", str(row['result_col'])])
        df_output[comp_name] = compare_criterium(row['result_col'],
                                                        row['operator'],
                                                        row['criterium_col'],
                                                        df_results)
        df_output[row['result_col']] = df_results[row['result_col']]
        df_output[operator_name] = row['operator']
        df_output[row['criterium_col']] = df_results[row['criterium_col']]
    
    return df_output

def main(args):
    df_verification = read_verification_df(args.verification)

    # Currently, need either QC_report.xlsx or otherwise Quast AND bbtools
    if args.qc_report is not None:
        df_merged = use_qc_report(args.qc_report, df_verification)
    elif (args.quast is not None) and (args.bbtools is not None):
        df_merged = use_quast_and_bbtools(args.quast, args.bbtools, df_verification)
    else:
        raise ValueError("QC report, quast multireport and bbtools multireport were not provided. I need either (the QC report) or (the quast and bbtools reports)")
    
    # Add typing if available
    if args.typing_report is not None:
        df_merged = add_typing_report(df_merged, args.typing_report)

    df_output = compare_to_criteria(df_merged, args.config)
    df_output.to_csv(args.output, sep='\t', index=False)

if __name__ == "__main__":
    main(args)



