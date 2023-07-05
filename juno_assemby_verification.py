from base_juno_pipeline import *
import argparse
import os
import pathlib
import sys
import yaml

from version import __package_name__, __version__, __description__

class JunoAssemblyVerificationRun(base_juno_pipeline.PipelineStartup,
                                  base_juno_pipeline.RunSnakemake):
    def __init__(
        self,
        input_dir,
        output_dir,
        input_type="fasta",
        cores=300,
        time_limit=60,
        local=False,
        queue='bio',
        unlock=False,
        rerunincomplete=False,
        dryrun=False,
        run_in_container=False,
        prefix=None,
        **kwargs
    ):
        output_dir = pathlib.Path(output_dir).resolve()
        workdir = pathlib.Path(__file__).parent.resolve()
        self.path_to_audit = output_dir.joinpath('audit_trail')
        base_juno_pipeline.PipelineStartup.__init__(
            self,
            input_dir=pathlib.Path(input_dir).resolve(),
            input_type="fasta",
        )
        base_juno_pipeline.RunSnakemake.__init__(
            self,
            pipeline_name=__package_name__,
            pipeline_version=__version__,
            output_dir=output_dir,
            workdir=pathlib.Path(__file__).parent.resolve(),
            cores=cores,
            local=local,
            time_limit=time_limit,
            queue=queue,
            unlock=unlock,
            rerunincomplete=rerunincomplete,
            dryrun=dryrun,
            useconda=not run_in_container,
            conda_prefix=prefix if not run_in_container else None,
            usesingularity=run_in_container,
            singularityargs=f"--bind {self.input_dir}:{self.input_dir} --bind {output_dir}:{output_dir}" if run_in_container else "",
            singularity_prefix=prefix if run_in_container else None,
            restarttimes=1,
            latency_wait=60,
            name_snakemake_report=str(
                self.path_to_audit.joinpath("juno_assembly_verification_report.html")
            ),
            **kwargs,
        )

        self.run_juno_assembly_verification_pipeline()


    # def update_sample_dict_with_metadata(self):
    #     self.__check_genus_is_supported()
    #     self.get_metadata_from_csv_file(filepath=self.metadata_file, expected_colnames=['sample', 'genus'])
    #     for sample in self.sample_dict:
    #         try:
    #             self.sample_dict[sample]['genus'] = self.juno_metadata[sample]['genus'].strip().lower()
    #         except (KeyError, TypeError):
    #             self.sample_dict[sample]['genus'] = self.genus

    def start_juno_assembly_pipeline(self):
        """
        Function to start the pipeline (some steps from PipelineStartup need to
        be modified for the Juno_assembly pipeline to accept metadata
        """
        self.start_juno_pipeline()
        #self.update_sample_dict_with_metadata()
        with open(self.sample_sheet, 'w') as file:
            yaml.dump(self.sample_dict, file, default_flow_style=False)
    
    def write_userparameters(self):
        config_params = {'input_dir': str(self.input_dir),
                        'out': str(self.output_dir),
                        'run_in_container': self.usesingularity}
        
        with open(self.user_parameters, 'w') as file:
            yaml.dump(config_params, file, default_flow_style=False)

        return config_params

    def run_juno_assembly_verification_pipeline(self):
        self.start_juno_assembly_pipeline()
        self.user_params = self.write_userparameters()
        self.get_run_info()
        self.successful_run = self.run_snakemake()
        assert self.successful_run, f'Please check the log files'
        if not self.dryrun or self.unlock:
            self.make_snakemake_report()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Juno assembly verification pipeline."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        required=True,
        metavar="DIR",
        help="Relative or absolute path to the input directory. It must either be the output directory of the Juno-assembly pipeline or it must contain all the raw reads (fastq) and assemblies (fasta) files for all samples to be processed.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        metavar="DIR",
        default="output",
        help="Relative or absolute path to the output directory. If non is given, an 'output' directory will be created in the current directory.",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="Running pipeline locally (instead of in a computer cluster). Default is running it in a cluster.",
    )
    parser.add_argument(
        "--no-containers",
        action = 'store_false',
        help = "Use conda environments instead of containers."
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type = str,
        metavar="PATH",
        default=None,
        help = "Conda or singularity prefix. Basically a path to the place where you want to store the conda environments or the singularity images."
    )
    parser.add_argument(
        "-q",
        "--queue",
        type = str,
        metavar = "STR",
        default = 'bio',
        help = 'Name of the queue that the job will be submitted to if working on a cluster.'
    )
    parser.add_argument(
        "-c",
        "--cores",
        type = int,
        metavar = "INT",
        default = 300 if not '--local' in sys.argv else 4,
        help="Number of cores to use. Default is 4 if running locally (--local) or 300 otherwise."
    )
    parser.add_argument(
        "-tl",
        "--time-limit",
        type = int,
        metavar = "INT",
        default = 60,
        help="Time limit per job in minutes (passed as -W argument to bsub). Jobs will be killed if not finished in this time."
    )
    parser.add_argument(
        "-rd",
        "--reference-directory",
        type = pathlib.Path,
        metavar = "DIR",
        default = pathlib.Path("/mnt/db/juno/assembly_verification/ref_typing"),
        help="Directory where reference typing data is stored"
    )
    parser.add_argument(
        "-cd",
        "--config-directory",
        type = pathlib.Path,
        metavar = "DIR",
        default = pathlib.Path("/mnt/db/juno/assembly_verification/config"),
        help="Directory where configuration files are stored"
    )
    # Snakemake arguments
    parser.add_argument(
        "-u",
        "--unlock",
        action="store_true",
        help="Unlock output directory (passed to snakemake).",
    )
    parser.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="Dry run printing steps to be taken in the pipeline without actually running it (passed to snakemake).",
    )
    parser.add_argument(
        "--rerunincomplete",
        action="store_true",
        help="Re-run jobs if they are marked as incomplete (passed to snakemake).",
    )
    parser.add_argument(
        "--snakemake-args",
        nargs="*",
        default={},
        action=helper_functions.SnakemakeKwargsAction,
        help="Extra arguments to be passed to snakemake API (https://snakemake.readthedocs.io/en/stable/api_reference/snakemake.html).",
    )
    args = parser.parse_args()
    juno_assembly_verification_run = JunoAssemblyVerificationRun(
        input_dir=args.input,
        output_dir=args.output,
        reference_dir=args.reference_directory,
        config_dir=args.config_directory,
        cores=args.cores,
        time_limit=args.time_limit,
        local=args.local,
        queue=args.queue,
        unlock=args.unlock,
        rerunincomplete=args.rerunincomplete,
        run_in_container=args.no_containers,
        prefix=args.prefix,
        dryrun=args.dryrun,
        **args.snakemake_args,
    )
