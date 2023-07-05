rule collect_and_rename:
    input:
        assemblies = [SAMPLES[sample]['assembly'] for sample in AMR_SAMPLES],
        log_pipeline = INPUT + "/audit_trail/log_pipeline.yaml"
    output:
        directory(OUT + "/de_novo_assembly_filtered")
    log:
        OUT + "/log/collect_and_rename.log",
    shell:
        """
python workflow/scripts/batch_rename.py \
  --input {input.assemblies} \
  --output {output} \
  --log-pipeline {input.log_pipeline} 2>&1>{log}
        """
    