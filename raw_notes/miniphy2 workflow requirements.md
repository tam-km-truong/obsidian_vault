snakemake
ete3
attotree
xopen

readme step:

srun --cpus-per-task=15 --mem=8G --pty bash

split -l 4000 -d -a 2 --additional-suffix=.txt accession_order.txt batches/part_

sed -i 's|^|/projects/reall/tam/data/661k/uncompressed_fastas/|'

snakemake --snakefile workflow/Snakefile_no_tree --cores 20 --config input_dir=/projects/reall/tam/data/661k/s_enterica_100k_experiment/s10k/batches/subdir_1 output_dir=/projects/reall/tam/data/661k/s_enterica_100k_experiment/s10k/cpr_files

######################
create batches

python workflow/scripts/create_batches.py workflow/tmp/metadata/bakrep-export_18112024.tsv.xz -s gtdbtk.classification.species -f '#id' -d workflow/tmp/batches/

###################
python workflow/scripts/find_genome_paths.py workflow/tmp/batches/ /Users/ktruong/data/661k/gziped_full/ --inplace

python find_genome_paths.py input/text_files/ input/genomes_flat/ --output output/text_files/ --no-recursion --file-extension fa`

python workflow/scripts/find_genome_paths.py /projects/reall/tam/data/661k/bakrep_batches/ /projects/reall/tam/data/661k/uncompressed_fastas/ --inplace --no-recursion --file-extension fa

###################

python ./workflow/scripts/split_folder.py /projects/reall/tam/data/661k/bakrep_batches/ 5

run snakemake on subdir

