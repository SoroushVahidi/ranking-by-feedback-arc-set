#!/bin/bash

#!/bin/bash

#SBATCH --job-name=rank_all

#SBATCH --partition=general

#SBATCH --account=ikoutis

#SBATCH --qos=standard

#SBATCH --nodes=1

#SBATCH --ntasks=1

#SBATCH --cpus-per-task=32

#SBATCH --mem=120G

#SBATCH --time=2-00:00:00

#SBATCH --output=slurm_logs/%x_%j.out

#SBATCH --error=slurm_logs/%x_%j.err



set -euo pipefail



cd /mmfs1/home/sv96/ranking\ by\ feedback\ arc\ set/GNNRank-main

mkdir -p slurm_logs logs_suite paper_csv



# If compute nodes don't inherit your conda env, uncomment and set it:

# source /apps/easybuild/software/Anaconda3/2023.09-0/etc/profile.d/conda.sh

# conda activate base



# Build dataset list: originals + all auto-wrapped adj datasets

DATASETS=("Dryad_animal_society" "finance")

while IFS= read -r d; do

  # train.py expects dataset string relative to data/, so these are "_AUTO/<name>"

  DATASETS+=("_AUTO/$d")

done < inventory/auto_datasets.txt



METHODS=(

  "SpringRank"

  "serialRank"

  "btl"

  "davidScore"

  "eigenvectorCentrality"

  "PageRank"

  "rankCentrality"

  "syncRank"

  "mvr"

  "SVD_RS"

  "SVD_NRS"

  "OURS_MFAS_INS1"

  "OURS_MFAS_INS2"

  "OURS_MFAS_INS3"

)



NUM_TRIALS=1

SEEDS="1"



echo "START $(date)"

python -V



for ds in "${DATASETS[@]}"; do

  for m in "${METHODS[@]}"; do

    safe_ds="${ds//\//__}"

    echo "RUN dataset=$ds method=$m  $(date)"

    python -u src/train.py --dataset "$ds" --all_methods "$m" --num_trials "$NUM_TRIALS" --seeds $SEEDS -SavePred \

      > "logs_suite/${safe_ds}__${m}.log" 2>&1 || echo "FAILED dataset=$ds method=$m (see logs_suite/${safe_ds}__${m}.log)"

  done

done



# Build cleaned paper table

python - <<'PY'

import os, glob, csv

import numpy as np



ROOT=os.getcwd()

OUTDIR=os.path.join(ROOT,"paper_csv")

os.makedirs(OUTDIR, exist_ok=True)



def is_combo_method(name:str)->bool:

    return ("SpringRanksyncRankserialRank" in name) or (len(name) > 60 and "SpringRank" in name and "syncRank" in name)



def parse_config_from_filename(path:str)->str:

    base=os.path.basename(path)

    return base[:-4] if base.endswith(".npy") else base



rows=[]



for ds_dir in sorted(glob.glob(os.path.join(ROOT,"result_arrays","*"))):

    if not os.path.isdir(ds_dir):

        continue

    dataset=os.path.basename(ds_dir)

    for which in ["upset","upset_latest"]:

        updir=os.path.join(ds_dir,which)

        if not os.path.isdir(updir):

            continue

        for method in sorted(os.listdir(updir)):

            if is_combo_method(method):

                continue

            mdir=os.path.join(updir,method)

            if not os.path.isdir(mdir):

                continue

            npys=sorted(glob.glob(os.path.join(mdir,"*.npy")))

            if not npys:

                continue

            if method == "DIGRACib":

                for npy in npys:

                    a=np.load(npy)

                    if not (a.ndim==3 and a.shape[-1]==3):

                        continue

                    vals=a.reshape(-1,3)

                    rows.append([dataset,method,parse_config_from_filename(npy),which,vals.shape[0],

                                float(np.nanmean(vals[:,0])), float(np.nanstd(vals[:,0])),

                                float(np.nanmean(vals[:,1])), float(np.nanstd(vals[:,1])),

                                float(np.nanmean(vals[:,2])), float(np.nanstd(vals[:,2])),

                                os.path.relpath(npy, ROOT)])

                continue

            for npy in npys:

                a=np.load(npy)

                a=np.asarray(a)

                if a.ndim==3 and a.shape[-1]==3:

                    vals=a.reshape(-1,3)

                elif a.ndim==2 and a.shape[1]==3:

                    vals=a

                elif a.ndim==1 and a.size==3:

                    vals=a.reshape(1,3)

                else:

                    continue

                rows.append([dataset,method,"" if len(npys)==1 else parse_config_from_filename(npy),which,vals.shape[0],

                            float(np.nanmean(vals[:,0])), float(np.nanstd(vals[:,0])),

                            float(np.nanmean(vals[:,1])), float(np.nanstd(vals[:,1])),

                            float(np.nanmean(vals[:,2])), float(np.nanstd(vals[:,2])),

                            os.path.relpath(npy, ROOT)])



out=os.path.join(OUTDIR,"results_table_clean.csv")

with open(out,"w",newline="") as f:

    w=csv.writer(f)

    w.writerow(["dataset","method","config","which","n",

                "upset_simple_mean","upset_simple_std",

                "upset_ratio_mean","upset_ratio_std",

                "upset_naive_mean","upset_naive_std",

                "source_file"])

    w.writerows(rows)

print("WROTE:", out, "ROWS:", len(rows))

PY



echo "DONE $(date)"

