#!/bin/bash



#SBATCH --job-name=ranking_dryrun

#SBATCH --output=dryrun_%j.out

#SBATCH --error=dryrun_%j.err

#SBATCH --time=01:00:00

#SBATCH --mem=16GB

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=4

#SBATCH --partition=general

# #SBATCH --qos=standard   # Uncomment and set to your cluster's QOS if needed



export PATH=/apps/easybuild/software/Anaconda3/2023.09-0/bin:$PATH

source activate feedback-weighted-maximization



cd "/mmfs1/home/sv96/ranking by feedback arc set/GNNRank-main"



rm -rf src/__pycache__/



DATASET="animal"



echo "============================================"

echo "DRY RUN: btl on $DATASET"

echo "============================================"

python -u src/train.py --dataset $DATASET --all_methods btl --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code for btl: $?"

echo ""

sleep 2



echo "============================================"

echo "DRY RUN: SpringRank on $DATASET"

echo "============================================"

python -u src/train.py --dataset $DATASET --all_methods SpringRank --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code for SpringRank: $?"

echo ""

sleep 2



echo "============================================"

echo "DRY RUN: OURS_MFAS_INS1 on $DATASET"

echo "============================================"

python -u src/train.py --dataset $DATASET --all_methods OURS_MFAS_INS1 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code for OURS_MFAS_INS1: $?"

echo ""

sleep 2



echo "============================================"

echo "DRY RUN: OURS_MFAS_INS3 on $DATASET"

echo "============================================"

python -u src/train.py --dataset $DATASET --all_methods OURS_MFAS_INS3 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code for OURS_MFAS_INS3: $?"

echo ""

sleep 2



echo "============================================"

echo "Dry run completed."

echo "============================================"
