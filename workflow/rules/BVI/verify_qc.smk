rule verify_accuracy_BVI:
    input:
        verification = config["config_dir"] + "/verification_criteria_BVI.tsv",
        qc_report = INPUT + "/Juno_assembly_QC_report/QC_report.xlsx",
        config = config["config_dir"] + "/config_BVI.tsv",
    output:
        tsv = OUT + "/verification_subreports/verify_accuracy_BVI.tsv"
    log:
        OUT + "/log/verify_qc_BVI.log",
    shell:
        """
python workflow/scripts/verify_accuracy.py \
  --verification {input.verification} \
  --qc-report {input.qc_report} \
  --config {input.config} \
  --output {output.tsv} 2>&1>{log}
        """