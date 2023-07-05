rule resfinder:
    input:
        assembly = lambda wildcards: SAMPLES[wildcards.sample]["assembly"],
    output:
        OUT + "/typing/resfinder/{sample}/ResFinder_results_tab.txt"
    message:
        "Running ResFinder on {wildcards.sample}."
    container:
        "docker://genomicepidemiology/resfinder:4.3.1"
    threads: config["threads"]["typing"]
    resources:
        mem_gb=config["mem_gb"]["typing"],
    log:
        OUT + "/log/typing/resfinder/{sample}.log",
    params:
        outdir = OUT + "/typing/resfinder/{sample}"
    shell:
        """
python -m resfinder -ifa {input.assembly} \
  -o {params.outdir} \
  -acq \
  -l 0.9 \
  -t 0.9 2>&1>{log}
        """

rule plasmidfinder:
    input:
        assembly = lambda wildcards: SAMPLES[wildcards.sample]["assembly"],
    output:
        OUT + "/typing/plasmidfinder/{sample}/results_tab.tsv"
    message:
        "Running PlasmidFinder on {wildcards.sample}."
    container:
        "docker://staphb/plasmidfinder:2.1.6"
    threads: config["threads"]["typing"]
    resources:
        mem_gb=config["mem_gb"]["typing"],
    params:
        outdir = OUT + "/typing/plasmidfinder/{sample}"
    log:
        OUT + "/log/typing/plasmidfinder/{sample}.log",
    shell:
        """
mkdir -p {params.outdir}
plasmidfinder.py -i {input.assembly} \
  -o {params.outdir} \
  -x \
  -l 0.9 \
  -t 0.9 2>&1>{log}
        """

rule select_cols_resfinder:
    input:
        OUT + "/typing/resfinder/{sample}/ResFinder_results_tab.txt"
    output:
        OUT + "/typing/resfinder_data/{sample}.tsv"
    params:
        columns = "Resistance gene,Identity,Coverage,Accession no."
    log:
        OUT + "/log/typing/select_cols_resfinder/{sample}.log",
    shell:
        """
python workflow/scripts/select_relevant_cols.py \
  -i {input} \
  -o {output} \
  -c "{params.columns}" 2>&1>{log}
        """
        
rule select_cols_plasmidfinder:
    input:
        OUT + "/typing/plasmidfinder/{sample}/results_tab.tsv"
    output:
        OUT + "/typing/plasmidfinder_data/{sample}.tsv"
    params:
        columns = "Plasmid,Identity,Query / Template length,Accession number"
    log:
        OUT + "/log/typing/select_cols_plasmidfinder/{sample}.log",
    shell:
        """
python workflow/scripts/select_relevant_cols.py \
  -i {input} \
  -o {output} \
  -c "{params.columns}" 2>&1>{log}
        """

rule get_hashes_resfinder:
    input:
        resfinder = expand(OUT + "/typing/resfinder_data/{sample}.tsv", sample=AMR_SAMPLES),
    output:
        OUT + "/typing/resfinder_hashes.txt"
    log:
        OUT + "/log/get_hashes_resfinder.log",
    shell:
        """
sha256sum {input} > {output} 2>{log}
        """

rule get_hashes_plasmidfinder:
    input:
        plasmidfinder = expand(OUT + "/typing/plasmidfinder_data/{sample}.tsv", sample=AMR_SAMPLES),
    output:
        OUT + "/typing/plasmidfinder_hashes.txt"
    log:
        OUT + "/log/get_hashes_plasmidfinder.log",
    shell:
        """
sha256sum {input} > {output} 2>{log}
        """

rule typing_report:
    input:
        rf = OUT + "/typing/resfinder_hashes.txt",
        pf = OUT + "/typing/plasmidfinder_hashes.txt",
    output:
        OUT + "/typing/typing_report.tsv"
    message:
        "Combinging typing results"
    log:
        OUT + "/log/typing_report.log",
    shell:
        """
python workflow/scripts/compare_typing.py \
  --resfinder {input.rf} \
  --plasmidfinder {input.pf} \
  --output {output} 2>&1>{log}
        """
        
