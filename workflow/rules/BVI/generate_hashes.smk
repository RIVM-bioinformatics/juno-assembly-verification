rule generate_assembly_hash:
    input:
        [BVI_SAMPLES[sample]['assembly'] for sample in BVI_SAMPLES]
    output:
        OUT + "/verification_subreports/BVI_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_clean_reads_hash:
    input:
        r1 = [BVI_SAMPLES[sample]['R1'] for sample in BVI_SAMPLES],
        r2 = [BVI_SAMPLES[sample]['R2'] for sample in BVI_SAMPLES],
    output:
        OUT + "/verification_subreports/BVI_clean_reads_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_id_species_hash:
    input:
        expand(INPUT + "/identify_species/{sample}", sample=BVI_SAMPLES),
    output:
        OUT + "/verification_subreports/BVI_id_species_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """

rule generate_qc_assembly_hash:
    input:
        INPUT + "/qc_de_novo_assembly/quast/report.tsv"
    output:
        OUT + "/verification_subreports/BVI_qc_assembly_hashes.txt"
    shell:
        """
sha256sum {input} > {output}
        """