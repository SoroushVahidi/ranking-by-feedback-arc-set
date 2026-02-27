#!/bin/bash



#SBATCH --job-name=final_dryrun

#SBATCH --output=final_dryrun_%j.out

#SBATCH --error=final_dryrun_%j.err

#SBATCH --time=02:00:00

#SBATCH --mem=32GB

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=8

#SBATCH --partition=general

# #SBATCH --qos=standard   # Uncomment and set to your cluster's QOS if needed



export PATH=/apps/easybuild/software/Anaconda3/2023.09-0/bin:$PATH

source activate feedback-weighted-maximization



cd "/mmfs1/home/sv96/ranking by feedback arc set/GNNRank-main"



rm -rf src/__pycache__/



echo "========== TEST 1: Baseline on small dataset (animal) =========="

python -u src/train.py --dataset animal --all_methods btl --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 2: Our method on small dataset (animal) =========="

python -u src/train.py --dataset animal --all_methods OURS_MFAS_INS1 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 3: GNN DIGRAC on small dataset (animal) =========="

python -u src/train.py --dataset animal --all_methods DIGRAC --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 4: GNN ib on small dataset (animal) =========="

python -u src/train.py --dataset animal --all_methods ib --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 5: mvr on small dataset (animal) =========="

python -u src/train.py --dataset animal --all_methods mvr --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 6: Baseline on medium dataset (HeadToHead) =========="

python -u src/train.py --dataset HeadToHead --all_methods btl --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 7: Our method on medium dataset (HeadToHead) =========="

python -u src/train.py --dataset HeadToHead --all_methods OURS_MFAS_INS3 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 8: Temporal dataset (basketball season 2009) =========="

python -u src/train.py --dataset basketball --season 2009 --all_methods btl --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 9: Our method on temporal (basketball 2009) =========="

python -u src/train.py --dataset basketball --season 2009 --all_methods OURS_MFAS_INS1 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 10: Football dataset =========="

python -u src/train.py --dataset football --season 2009 --all_methods OURS_MFAS_INS3 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 11: Finance (largest dataset) =========="

python -u src/train.py --dataset finance --all_methods btl --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 12: Our method on finance (largest) =========="

python -u src/train.py --dataset finance --all_methods OURS_MFAS_INS1 --num_trials 1 --seeds 10 --debug --SavePred

echo "Exit code: $?"

echo ""



echo "========== TEST 13: Check runtime files were saved =========="

find ./result_arrays/debug -name "*.npy" -newer dry_run_final.sh 2>/dev/null | head -30

echo ""

find ./result_arrays/debug -path "*/runtime/*" -name "*.npy" 2>/dev/null

echo ""



echo "========== ALL TESTS COMPLETED =========="
