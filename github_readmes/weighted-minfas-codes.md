# Weighted MinFAS Codes

Code to **reproduce experiments** for a **local-ratio heuristic** for the **minimal (minimum) feedback arc set** problem in **weighted directed graphs**, using instances from **DIMACS** and other graph benchmarks.

## Reference

- **Problem:** Minimal feedback arc set (FAS) in weighted directed graphs.  
- **Benchmarks:** DIMACS / graph-benchmarks.  
- **Method:** Local-ratio heuristic as implemented in this repo. See the paper or report associated with this code for the algorithm description and experimental setup.

## What is in this repo

- Implementation of the local-ratio heuristic for weighted FAS.
- Scripts to run on DIMACS (or other) instances.
- Instructions to reproduce the paper or report figures (if applicable).

## How to run

1. Clone the repo and install dependencies (C++/Python, graph I/O).
2. Download or prepare DIMACS graph instances (see project docs).
3. Run the main program or script and collect results (e.g. solution cost, runtime).

## License

See the LICENSE file in the repository. For academic use, please cite the paper or report associated with this heuristic and this repository.
