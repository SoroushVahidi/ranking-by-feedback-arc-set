#!/bin/bash



#SBATCH --job-name=ranking_full

#SBATCH --output=full_%j.out

#SBATCH --error=full_%j.err

#SBATCH --time=72:00:00

#SBATCH --mem=100GB

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=48

#SBATCH --partition=general

#SBATCH --qos=standard



export PATH=/apps/easybuild/software/Anaconda3/2023.09-0/bin:$PATH

source activate feedback-weighted-maximization



cd "/mmfs1/home/sv96/ranking by feedback arc set/GNNRank-main"



rm -rf src/__pycache__/



# =============================================================================

# METHOD GROUPS

# =============================================================================

ALL_NON_NN="SpringRank syncRank serialRank btl davidScore eigenvectorCentrality PageRank rankCentrality SVD_RS SVD_NRS OURS_MFAS_INS1 OURS_MFAS_INS2 OURS_MFAS_INS3 OURS_MFAS"

GNN_METHODS="DIGRAC ib"

TRIALS=10



echo "========== STARTING FULL EXPERIMENTS =========="

echo "Date: $(date)"

echo "78 datasets, all methods, $TRIALS trials each"

echo ""



# =============================================================================

# PART 1: STATIC DATASETS (6 datasets)

# =============================================================================

STATIC="animal HeadToHead finance faculty_business faculty_cs faculty_history"

SMALL_STATIC="animal faculty_business faculty_cs faculty_history"



for dataset in $STATIC

do

    echo "############### DATASET: $dataset ###############"



    # Non-NN methods

    for method in $ALL_NON_NN

    do

        echo "[$(date +%H:%M:%S)] $method on $dataset"

        python -u src/train.py --dataset $dataset --all_methods $method --num_trials $TRIALS --seeds 10 --SavePred

        echo "Exit code: $?"

    done



    # GNN methods (DIGRAC, ib) — train_with=dist (GNNRank-N style)

    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (dist) on $dataset"

        python -u src/train.py --dataset $dataset --all_methods $method --num_trials $TRIALS --seeds 10 --train_with dist --SavePred

        echo "Exit code: $?"

    done



    # GNN methods — train_with=proximal_baseline (GNNRank-P style)

    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (proximal_baseline) on $dataset"

        python -u src/train.py --dataset $dataset --all_methods $method --num_trials $TRIALS --seeds 10 --train_with proximal_baseline --trainable_alpha --pretrain_with dist --pretrain_epochs 50 --SavePred

        echo "Exit code: $?"

    done

done



# MVR only on small datasets (times out on HeadToHead, Finance, Basketball)

for dataset in $SMALL_STATIC

do

    echo "[$(date +%H:%M:%S)] mvr on $dataset"

    python -u src/train.py --dataset $dataset --all_methods mvr --num_trials $TRIALS --seeds 10 --SavePred

    echo "Exit code: $?"

done



# =============================================================================

# PART 2: BASKETBALL 1985-2014 (30 seasons)

# =============================================================================

echo "############### BASKETBALL 1985-2014 ###############"

for season in $(seq 1985 2014)

do

    for method in $ALL_NON_NN

    do

        echo "[$(date +%H:%M:%S)] $method on basketball $season"

        python -u src/train.py --dataset basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (dist) on basketball $season"

        python -u src/train.py --dataset basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with dist --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (proximal_baseline) on basketball $season"

        python -u src/train.py --dataset basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with proximal_baseline --trainable_alpha --pretrain_with dist --pretrain_epochs 50 --SavePred

        echo "Exit code: $?"

    done

done



# =============================================================================

# PART 3: FINER BASKETBALL 1985-2014 (30 seasons)

# =============================================================================

echo "############### FINER BASKETBALL 1985-2014 ###############"

for season in $(seq 1985 2014)

do

    for method in $ALL_NON_NN

    do

        echo "[$(date +%H:%M:%S)] $method on finer_basketball $season"

        python -u src/train.py --dataset finer_basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (dist) on finer_basketball $season"

        python -u src/train.py --dataset finer_basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with dist --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (proximal_baseline) on finer_basketball $season"

        python -u src/train.py --dataset finer_basketball --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with proximal_baseline --trainable_alpha --pretrain_with dist --pretrain_epochs 50 --SavePred

        echo "Exit code: $?"

    done

done



# =============================================================================

# PART 4: FOOTBALL 2009-2014 (6 seasons)

# =============================================================================

echo "############### FOOTBALL 2009-2014 ###############"

for season in $(seq 2009 2014)

do

    for method in $ALL_NON_NN

    do

        echo "[$(date +%H:%M:%S)] $method on football $season"

        python -u src/train.py --dataset football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --SavePred

        echo "Exit code: $?"

    done



    echo "[$(date +%H:%M:%S)] mvr on football $season"

    python -u src/train.py --dataset football --season $season --all_methods mvr --num_trials $TRIALS --seeds 10 --SavePred

    echo "Exit code: $?"



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (dist) on football $season"

        python -u src/train.py --dataset football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with dist --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (proximal_baseline) on football $season"

        python -u src/train.py --dataset football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with proximal_baseline --trainable_alpha --pretrain_with dist --pretrain_epochs 50 --SavePred

        echo "Exit code: $?"

    done

done



# =============================================================================

# PART 5: FINER FOOTBALL 2009-2014 (6 seasons)

# =============================================================================

echo "############### FINER FOOTBALL 2009-2014 ###############"

for season in $(seq 2009 2014)

do

    for method in $ALL_NON_NN

    do

        echo "[$(date +%H:%M:%S)] $method on finer_football $season"

        python -u src/train.py --dataset finer_football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --SavePred

        echo "Exit code: $?"

    done



    echo "[$(date +%H:%M:%S)] mvr on finer_football $season"

    python -u src/train.py --dataset finer_football --season $season --all_methods mvr --num_trials $TRIALS --seeds 10 --SavePred

    echo "Exit code: $?"



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (dist) on finer_football $season"

        python -u src/train.py --dataset finer_football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with dist --SavePred

        echo "Exit code: $?"

    done



    for method in $GNN_METHODS

    do

        echo "[$(date +%H:%M:%S)] $method (proximal_baseline) on finer_football $season"

        python -u src/train.py --dataset finer_football --season $season --all_methods $method --num_trials $TRIALS --seeds 10 --train_with proximal_baseline --trainable_alpha --pretrain_with dist --pretrain_epochs 50 --SavePred

        echo "Exit code: $?"

    done

done



echo ""

echo "========== ALL EXPERIMENTS COMPLETED =========="

echo "Date: $(date)"

echo ""



# =============================================================================

# SUMMARY

# =============================================================================

echo "===== RESULT FILES CREATED ====="

echo "Runtime files:"

find ./result_arrays -path "*/runtime/*" -name "*.npy" ! -path "*/debug/*" | wc -l

echo "Upset files:"

find ./result_arrays -path "*/upset/*" -name "*.npy" ! -path "*/debug/*" | wc -l

echo "Kendall tau files:"

find ./result_arrays -path "*/kendalltau/*" -name "*.npy" ! -path "*/debug/*" | wc -l
