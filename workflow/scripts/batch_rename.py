#!/usr/bin/env python3

import pathlib
import shutil

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--input",
                    help="Input assemblies",
                    type=pathlib.Path,
                    nargs="+",
                    required=True)
parser.add_argument("--output",
                    help="Output directory with renamed assemblies",
                    type=pathlib.Path,
                    default="de_novo_assembly_filtered")
parser.add_argument("--log-pipeline",
                    help="log_pipeline.yaml from Juno-assembly",
                    type=pathlib.Path,
                    required=True)

args = parser.parse_args()

def get_version(log_pipeline_path : pathlib.Path) -> str:
    """
    Get version from Juno-assembly run.

    Args:
        log_pipeline_path: path to log_pipeline.yaml in audit_trail dir.
    
    Returns:
        Juno-assembly version as str
    """
    with open(log_pipeline_path) as log_pipeline:
        for line in log_pipeline.readlines():
            if line.startswith("pipeline_version:"): 
                return line.split(' ')[1].rstrip('\n')


def produce_new_name(assembly_path : pathlib.Path, pipeline_version : str) -> str:
    """
    Add Juno-assembly version to assembly name.

    Args:
        assembly_path: Path to assembly to rename
        pipeline_version: Juno-assembly version
    
    Returns:
        Assembly with Juno-assembly version added to file name.
    
    Raises:
        AssertionError: if no underscore is found in assembly name (AMR group-specific convention indicating organism)
    """
    assembly_name = assembly_path.stem
    before_first_underscore = assembly_name.split('_')[0]
    after_first_underscore = "_".join(assembly_name.split('_')[1:])
    assert len(after_first_underscore) > 0, f"Expected an underscore in {assembly_name}, but did not find any"
    new_assembly_name = f"{before_first_underscore}-version{pipeline_version}_{after_first_underscore}.fasta"
    return new_assembly_name

def copy_assembly(input_path : pathlib.Path, new_name : str, output_directory : pathlib.Path) -> None:
    """
    Copies renamed assembly to other dir.

    Args:
        input_path: path to assembly to rename
        new_name: file name (incl Juno-assembluy version)
        output_directory: dir where to save renamed assembly
    
    Returns:
        None
    """
    output_path = output_directory.joinpath(new_name)
    shutil.copy2(input_path, output_path)

def main(args):
    if not args.output.exists():
        args.output.mkdir()
    assembly_version = get_version(args.log_pipeline)
    for assembly_path in args.input:
        assembly_renamed = produce_new_name(assembly_path, assembly_version)
        copy_assembly(assembly_path, assembly_renamed, args.output)

if __name__ == "__main__":
    main(args)