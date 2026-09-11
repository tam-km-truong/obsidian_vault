Run mtuber atb recompression
snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/atb/recompression/mtuber/batches/ output_dir=/scratch/ktruong/data/atb/compression_results/recompressed_mtuber_5%_reference/ --cores 25 --rerun-incomplete

done with phylopacking ecoli 100% reference

compress the fixed fraction size

running with all batches fraction

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/060_ecoli_compress_at_point/batches/ output_dir=/scratch/ktruong/data/661k/060_ecoli_compress_at_point/compression_results/ --cores 25 ==> done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/batches_to_compress/binning_experiment/batches_ecoli_250mb/bins/ output_dir=/scratch/ktruong/data/661k/compression_results/batches_ecoli_250mb/ --cores 15 ==> miniphy compress error to be rerun

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/batches_fraction_all/subdir_2/ output_dir=/scratch/ktruong/data/661k/058_experiments/results_fraction/reordered_1k/ sketch_size=1000 --cores 45 ==> done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/atb/recompression/staph_aureus/batches/ output_dir=/scratch/ktruong/data/atb/compression_results/recompressed_saureus_5%_ref/ --cores 25 ==> running

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/e_coli_batches/ output_dir=/scratch/ktruong/data/661k/058_experiments/cmp_rslt_ecoli/2nd_reordered_1k/ sketch_size=1000 --cores 40 --rerun-incomplete

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/batches_fixed/subdir_2/ output_dir=/scratch/ktruong/data/661k/058_experiments/result_fixed/reordered_10k/ --cores 56 ==> done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/atb/recompression/staph_aureus/batches/ output_dir=/scratch/ktruong/data/atb/compression_results/recompressed_saureus_5%_ref/ --cores 25 => done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/atb/recompression/strep_pneumoniae/batches/ output_dir=/scratch/ktruong/data/atb/compression_results/recompressed_spneumoniae_5%_ref/ --cores 25 ==> done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/e_coli_batches/ output_dir=/scratch/ktruong/data/661k/058_experiments/cmp_rslt_ecoli/2nd_reordered_1k/ sketch_size=1000 --cores 40 --rerun-incomplete

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/atb/recompression/mtuber/batches_10%/ output_dir=/scratch/ktruong/data/atb/compression_results/recompressed_mtuber_10%_reference/ enable_compression=False --cores 25 --rerun-incomplete ==> done
 
 snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/batches_fixed/subdir_1/ output_dir=/scratch/ktruong/data/661k/058_experiments/result_fixed/reordered_10k/ --cores 50 --rerun-incomplete ==>done
 
snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/batches_fraction_all/subdir_1/ output_dir=/scratch/ktruong/data/661k/058_experiments/results_fraction/reordered_1k/ sketch_size=1000 --cores 45 --rerun-incomplete==>done

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/e_coli_batches/ output_dir=/scratch/ktruong/data/661k/058_experiments/cmp_rslt_ecoli/2nd_reordered_100/ sketch_size=100 --cores 50 ==> running

snakemake --snakefile workflow/Snakefile --config input_dir=/scratch/ktruong/data/661k/058_experiments/e_coli_batches/ output_dir=/scratch/ktruong/data/661k/058_experiments/cmp_rslt_ecoli/2nd_reordered_100/ sketch_size=100 --cores 50 --rerun-incomplete -n ==> to check