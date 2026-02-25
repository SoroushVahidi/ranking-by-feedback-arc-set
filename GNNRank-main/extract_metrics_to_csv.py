import re
import csv
import sys
from pathlib import Path


def parse_log(in_path: Path, which: str = "latest"):
    """
    Parse a GNNRank log (.out) and extract metrics tables.

    Parameters
    ----------
    in_path : Path
        Path to the .out file (e.g., full_833614.out).
    which : {"latest", "best"}
        Whether to parse the *_latestMetric or *_bestMetric tables.

    Returns
    -------
    rows : list[dict]
        One row per (dataset, method) pair with mean/std of each metric.
    """
    if which not in {"latest", "best"}:
        raise ValueError("which must be 'latest' or 'best'")

    target_suffix = "_latestMetric" if which == "latest" else "_bestMetric"

    metric_names = [
        "test_kendall_tau",
        "test_kendall_p",
        "val_kendall_tau",
        "val_kendall_p",
        "all_kendall_tau",
        "all_kendall_p",
        "upset_simple",
        "upset_ratio",
        "upset_naive",
        "runtime_sec",
    ]

    rows = []

    with in_path.open("r") as f:
        lines = f.readlines()

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip("\n")

        # Match header lines like:
        #   Dryad_animal_society/_latestMetric/Method    SpringRank
        #   finance/_bestMetric/Method    SpringRank
        #   Halo2BetaData/HeadToHead_bestMetric/Method    SpringRank
        #   Basketball_temporal/1985_bestMetric/Method    SpringRank
        dataset_full = None
        method = None

        # Case 1: <dataset>/_bestMetric/Method   <method>
        m1 = re.match(r"(\S+)/" + re.escape(target_suffix) + r"/Method\s+(\S+)", line)
        if m1:
            dataset_full = m1.group(1)
            method = m1.group(2)
        else:
            # Case 2: <prefix>/<dataset>_bestMetric/Method   <method>
            # e.g. Halo2BetaData/HeadToHead_bestMetric/Method
            #      Basketball_temporal/1985_bestMetric/Method
            m2 = re.match(r"(\S+)/(\S+)" + re.escape(target_suffix) + r"/Method\s+(\S+)", line)
            if m2:
                dataset_full = m2.group(1) + "/" + m2.group(2)
                method = m2.group(3)

        if dataset_full is None:
            i += 1
            continue
        metrics = {}

        i += 1
        # Scan until blank line or separator
        while i < n and lines[i].strip():
            l = lines[i].strip()

            # Lines can look like:
            # upset_simple                                0.50$\pm$0.00
            m2 = re.match(r"([a-zA-Z_]+)\s+([0-9.+\-eE]+)\$\\pm\$([0-9.+\-eE]+)", l)
            if m2:
                name_raw, mean_str, std_str = m2.group(1), m2.group(2), m2.group(3)
                # Map raw names into our standardized ones
                name_map = {
                    "test": "test_kendall_tau",
                    "test_kendall_tau": "test_kendall_tau",
                    "test_kendall_p": "test_kendall_p",
                    "val": "val_kendall_tau",
                    "val_kendall_tau": "val_kendall_tau",
                    "val_kendall_p": "val_kendall_p",
                    "all": "all_kendall_tau",
                    "all_kendall_tau": "all_kendall_tau",
                    "all_kendall_p": "all_kendall_p",
                    "upset_simple": "upset_simple",
                    "upset_ratio": "upset_ratio",
                    "upset_naive": "upset_naive",
                    "runtime_sec": "runtime_sec",
                }

                std_name = name_map.get(name_raw)
                if std_name in metric_names:
                    metrics[std_name] = (mean_str, std_str)

            i += 1

        # Only record if we found at least the main upset and runtime metrics
        required = ["upset_simple", "upset_ratio", "upset_naive", "runtime_sec"]
        if all(name in metrics for name in required):
            row = {
                "dataset": dataset_full,
                "method": method,
            }
            for name in metric_names:
                mean_key = f"{name}_mean"
                std_key = f"{name}_std"
                if name in metrics:
                    row[mean_key] = metrics[name][0]
                    row[std_key] = metrics[name][1]
                else:
                    row[mean_key] = ""
                    row[std_key] = ""
            rows.append(row)

        i += 1

    return rows


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_metrics_to_csv.py LOGFILE.out [which] [OUT.csv]")
        print("  which: latest (default) or best")
        sys.exit(1)

    in_path = Path(sys.argv[1])
    which = sys.argv[2] if len(sys.argv) >= 3 else "latest"

    if len(sys.argv) >= 4:
        out_path = Path(sys.argv[3])
    else:
        # Default to descriptive names like:
        #   full_833614_metrics_latest.csv
        #   full_833614_metrics_best.csv
        stem = in_path.stem  # e.g. "full_833614"
        suffix = f"_metrics_{which}.csv"
        out_path = in_path.with_name(stem + suffix)

    rows = parse_log(in_path, which=which)

    if not rows:
        print(f"No rows parsed from {in_path} for '{which}' tables.")
        sys.exit(0)

    # Decide which columns to keep:
    # - Always keep 'dataset' and 'method'
    # - For metric columns, drop any column that is empty for all rows
    metric_names = [
        "test_kendall_tau",
        "test_kendall_p",
        "val_kendall_tau",
        "val_kendall_p",
        "all_kendall_tau",
        "all_kendall_p",
        "upset_simple",
        "upset_ratio",
        "upset_naive",
        "runtime_sec",
    ]

    base_order = ["dataset", "method"]
    for name in metric_names:
        base_order.append(f"{name}_mean")
        base_order.append(f"{name}_std")

    # Collect all keys that actually appear, to avoid csv.DictWriter errors
    present_keys = {k for row in rows for k in row.keys()}

    fieldnames = []
    for key in base_order:
        if key not in present_keys:
            continue
        if key in ("dataset", "method"):
            fieldnames.append(key)
            continue
        # keep only if at least one row has a non-empty value
        if any(row.get(key) not in ("", None) for row in rows):
            fieldnames.append(key)

    # Trim rows to only include chosen fieldnames so csv.DictWriter
    # does not see unexpected keys.
    trimmed_rows = []
    for row in rows:
        trimmed = {}
        for key in fieldnames:
            if key in row:
                trimmed[key] = row[key]
        trimmed_rows.append(trimmed)

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trimmed_rows)

    print(f"Wrote {len(rows)} rows to {out_path}")

    # Additionally, write a dataset-level summary CSV:
    #   <logstem>_datasets.csv
    dataset_counts = {}
    for row in rows:
        ds = row.get("dataset", "")
        if ds not in dataset_counts:
            dataset_counts[ds] = set()
        method = row.get("method", "")
        if method:
            dataset_counts[ds].add(method)

    ds_rows = []
    for ds, methods in sorted(dataset_counts.items()):
        ds_rows.append(
            {
                "dataset": ds,
                "num_methods": len(methods),
            }
        )

    ds_out = in_path.with_name(in_path.stem + "_datasets.csv")
    with ds_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["dataset", "num_methods"])
        writer.writeheader()
        writer.writerows(ds_rows)

    print(f"Wrote {len(ds_rows)} dataset rows to {ds_out}")


if __name__ == "__main__":
    main()

