# Main run
rule generate_assembly_hash_main:
    input:
        expand(INPUT + "/de_novo_assembly_filtered/{sample}.fasta", sample=BVI_SAMPLES)
    output:
        OUT + "/verification_subreports/repeatability/main_run/BVI_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_clean_reads_hash_main:
    input:
        r1 = expand(INPUT + "/clean_fastq/{sample}_pR1.fastq.gz", sample=BVI_SAMPLES),
        r2 = expand(INPUT + "/clean_fastq/{sample}_pR2.fastq.gz", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/main_run/BVI_clean_reads_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_id_species_hash_main:
    input:
        expand(INPUT + "/identify_species/{sample}", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/main_run/BVI_id_species_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_qc_assembly_hash_main:
    input:
        INPUT + "/qc_de_novo_assembly/quast/report.tsv"
    output:
        OUT + "/verification_subreports/repeatability/main_run/BVI_qc_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

## First repeat
rule generate_assembly_hash_repeat_1:
    input:
        expand(REPEAT_1 + "/de_novo_assembly_filtered/{sample}.fasta", sample=BVI_SAMPLES)
    output:
        OUT + "/verification_subreports/repeatability/repeat_1/BVI_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_clean_reads_hash_repeat_1:
    input:
        r1 = expand(REPEAT_1 + "/clean_fastq/{sample}_pR1.fastq.gz", sample=BVI_SAMPLES),
        r2 = expand(REPEAT_1 + "/clean_fastq/{sample}_pR2.fastq.gz", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/repeat_1/BVI_clean_reads_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_id_species_hash_repeat_1:
    input:
        expand(REPEAT_1 + "/identify_species/{sample}", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/repeat_1/BVI_id_species_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_qc_assembly_hash_repeat_1:
    input:
        REPEAT_1 + "/qc_de_novo_assembly/quast/report.tsv"
    output:
        OUT + "/verification_subreports/repeatability/repeat_1/BVI_qc_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

## Second repeat
rule generate_assembly_hash_repeat_2:
    input:
        expand(REPEAT_2 + "/de_novo_assembly_filtered/{sample}.fasta", sample=BVI_SAMPLES)
    output:
        OUT + "/verification_subreports/repeatability/repeat_2/BVI_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_clean_reads_hash_repeat_2:
    input:
        r1 = expand(REPEAT_2 + "/clean_fastq/{sample}_pR1.fastq.gz", sample=BVI_SAMPLES),
        r2 = expand(REPEAT_2 + "/clean_fastq/{sample}_pR2.fastq.gz", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/repeat_2/BVI_clean_reads_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_id_species_hash_repeat_2:
    input:
        expand(REPEAT_2 + "/identify_species/{sample}", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/repeatability/repeat_2/BVI_id_species_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_qc_assembly_hash_repeat_2:
    input:
        REPEAT_2 + "/qc_de_novo_assembly/quast/report.tsv"
    output:
        OUT + "/verification_subreports/repeatability/repeat_2/BVI_qc_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """


rule compare_hashes:
    input:
        main = OUT + "/verification_subreports/repeatability/main_run/BVI_{analysis}_hashes.txt",
        repeat_1 = OUT + "/verification_subreports/repeatability/repeat_1/BVI_{analysis}_hashes.txt",
        repeat_2 = OUT + "/verification_subreports/repeatability/repeat_2/BVI_{analysis}_hashes.txt",
    output:
        summary = OUT + "/verification_subreports/repeatability/summary_{analysis}.txt",
        discrepancies = OUT + "/verification_subreports/repeatability/discrepancies_{analysis}.txt",
    params:
        analysis = "{analysis}"
    shell:
        """
python workflow/scripts/compare_hashes.py \
{input} \
--analysis {params.analysis} \
--discrepancies {output.discrepancies} \
> {output.summary}
        """