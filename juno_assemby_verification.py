from pathlib import Path
import pathlib
import yaml
import argparse
import sys
from dataclasses import dataclass, field
from juno_library import Pipeline
from typing import Optional, Tuple
from version import __package_name__, __version__, __description__

def main() -> None:
    juno_assembly_verification = JunoAssemblyVerificationRun()
    juno_assembly_verification.run()

@dataclass
class JunoAssemblyVerificationRun(Pipeline):
    pipeline_name: str = __package_name__
    pipeline_version: str = __version__
    input_type: str = "fasta"

    def _add_args_to_parser(self) -> None:
        super()._add_args_to_parser()

        self.parser.description = (
            "Juno assembly verification pipeline."
        )

        self.add_argument(
            "-r",
            "--repeats",
            type=pathlib.Path,
            required=True,
            metavar="DIR",
            help="Relative or absolute path to second and third repeats of Juno-assembly.",
            nargs=2,
        )
        
        self.add_argument(
            "-rd",
            "--reference-directory",
            type = pathlib.Path,
            metavar = "DIR",
            default = pathlib.Path("/mnt/db/juno/assembly_verification/ref_typing"),
            help="Directory where reference typing data is stored"
        )
        self.add_argument(
            "-cd",
            "--config-directory",
            type = pathlib.Path,
            metavar = "DIR",
            default = pathlib.Path("/mnt/db/juno/assembly_verification/config"),
            help="Directory where configuration files are stored"
        )

    def _parse_args(self) -> argparse.Namespace:
        args = super()._parse_args()

        # Optional arguments are loaded into self here
        self.repeats: Tuple[Path] = args.repeats,
        self.reference_dir: Path = args.reference_directory,
        self.config_dir: Path = args.config_directory,        

        return args
    
    def setup(self) -> None:
        super().setup()

        with open(
            Path(__file__).parent.joinpath("config/pipeline_parameters.yaml")
        ) as f:
            parameters_dict = yaml.safe_load(f)
        self.snakemake_config.update(parameters_dict)

        self.user_parameters = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "repeat_1": str(self.repeats[0][0].resolve()),
            "repeat_2": str(self.repeats[0][1].resolve()),
            "reference_dir": str(self.reference_dir),
            "config_dir": str(self.config_dir[0]),
            "use_singularity": str(self.snakemake_args["use_singularity"]),
        }
        
        if self.snakemake_args["use_singularity"]:
            self.snakemake_args["singularity_args"] = " ".join(
                [
                    self.snakemake_args["singularity_args"],
                    f"--bind {self.repeats[0][0]}:{self.repeats[0][0]}",
                    f"--bind {self.repeats[0][1]}:{self.repeats[0][1]}",
                ]  # paths that singularity should be able to read from can be bound by adding to the above list
            )

if __name__ == "__main__":
    main()