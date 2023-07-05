rule verify_accuracy_AMR:
    input:
        verification = config["config_dir"] +"/verification_criteria_AMR.tsv",
        quast = INPUT + "/qc_de_novo_assembly/quast/transposed_report.tsv",
        bbtools = INPUT + "/qc_de_novo_assembly/bbtools_scaffolds/bbtools_summary_report.tsv",
        qc_report = INPUT + "/Juno_assembly_QC_report/QC_report.xlsx",
        typing_report = OUT + "/typing/typing_report.tsv",
        config = config["config_dir"] + "/config_AMR.tsv",
    output:
        tsv = OUT + "/verification_subreports/verify_accuracy_AMR.tsv"
    shell:
        """
python workflow/scripts/verify_accuracy.py \
  --verification {input.verification} \
  --qc-report {input.qc_report} \
  --typing-report {input.typing_report} \
  --config {input.config} \
  --output {output.tsv}
        """

rule display_typing_discrepancies:
    input:
        typing = OUT + "/typing/typing_report.tsv",
        ref_typing = config["reference_dir"],
        tsv = OUT + "/verification_subreports/verify_qc_AMR.tsv",
    output:
        directory(OUT + "/discrepancies")
    params:
        typing_dir = OUT + "/typing"
    shell:
        """
python workflow/scripts/display_typing_discrepancies.py \
    --input {params.typing_dir} \
    --ref-input {input.ref_typing} \
    --verification {input.tsv} \
    --output {output}
        """