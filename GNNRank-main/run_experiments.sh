#!/bin/bash

#SBATCH --job-name=ranking_experiments
#SBATCH --output=results_%j.out
#SBATCH --error=results_%j.err
#SBATCH --time=72:00:00
#SBATCH --mem=100GB
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --partition=general
# #SBATCH --qos=standard   # Uncomment and set to your cluster's QOS if needed

# Set environment variables
export PATH=/apps/easybuild/software/Anaconda3/2023.09-0/bin:$PATH
source activate feedback-weighted-maximization

# Define the datasets and methods
DATASETS=("Dryad_animal_society" "finance" "Halo2BetaData") # Add more datasets as needed
METHODS=("SpringRank" "syncRank" "serialRank" "btl" "davidScore" "eigenvectorCentrality" "PageRank" "rankCentrality" "mvr" "SVD_RS" "SVD_NRS" "DIGRAC" "ib" "OURS_MFAS_INS1" "OURS_MFAS_INS2" "OURS_MFAS_INS3" "OURS_MFAS")

# Loop through datasets and methods
for dataset in "${DATASETS[@]}"
do
    for method in "${METHODS[@]}"
    do
        echo "Running $method on $dataset"
        
        # Run the experiment with --SavePred flag
        python -u src/train.py --dataset $dataset --all_methods $method --num_trials 1 --seeds 1 --SavePred

        # Wait a bit between runs (optional, to prevent overload)
        sleep 10
    done
done

echo "Experiments completed."