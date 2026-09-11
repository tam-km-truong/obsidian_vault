Presentation de Galaxy
	galaxy training network: more info here
	what is galaxy
		data analysis platform
		web based
			ez free open src (10k tools, 13k publications, many tuto)
			intutive, no cli, reproducible, cross-domain
			snakemake workflow and galaxy in the same basket
	how to use
		take an server
		interface see slides	
Intro generale d'assemblage
	slide de GTM
	genome assembly and assembly qc
	what is it: reconstructs the complete genome from reads
	consistes of aligning and recnstructing reads to form a continuous sequnece of a chromosomes or a set con contiguos seq (contig or scaffold)
	assembly vs alignment: one has reference (there are biases), assembly no reference but need more input
	steps before starting a genomes project
		1 info about the speciesL location overlap with indigenous people or local communities territories, expected genome size, ploidy micro-chromosomes, organell, what tdata is already available, from what databases
		2 talk to local people lol
		3 collaborator
		4 sampling is the key step, select the best possible DNA source and an optimal extraction procedure
		5 chose sequencing tech
		6 seq and assemble
	definitions
	contig: from long reads
	scaffold : from contigsusing paired read (Hi C) then create scaffolds, theres a gap
	assembly: set of contigs or scaffold
	different level of assembly:
		contig assembly
		scaffold assembly
		chromosome level assembly: 1 chromosome = 1 scaffold
		t2t telomere to telomere
	haplotig: contig from the same haplotypele
	primary assembly
	alternate assembly
	haplotype resolved assebly
	Computational ressources and requirements: different for each steps
	Data format:
		fasta
		fastq: is fasta with quality score
		sam: text based format originally for storing biological sequences aligned to a reference seuqnce
		bam: lossless compressed binary representation of the sam format (2 type bam mapped and bam unmapped)
		cram: compressed columnar file format
	Pacbio: des longreads
	continuity: N50
		![[Pasted image 20260203111412.png]]
		some tools: quast metaquast quast-Lg maquast icarus
	Completeness: BUSCO score (core genes in assembly)/(core genes in reference database)
	Correctness: proportion of the assembly that is free from mistakes
		align back reads to the assembly and check for inconsistencies
Annotation