# Hybrid Interval-Based Refinement for Large-Scale Weighted Feedback Arc Set

This repository contains code and experiments for a **hybrid interval-based refinement** approach to the **weighted feedback arc set (FAS)** problem at large scale. The method combines interval-based ideas with local refinement to obtain good solutions on large directed graphs.

## What's in this repo

- Implementation of the hybrid interval-based refinement algorithm for weighted FAS.
- Scripts or drivers to run on benchmark instances (e.g. DIMACS or other graph benchmarks).
- Optional comparison with other FAS heuristics or solvers.

## How to run

1. Clone the repository and install dependencies (e.g. C++/Python, graph libraries).
2. Build the project (see Makefile or build instructions in the repo).
3. Run on graph instances (edge list or format specified in the repo).

## Problem

In the **weighted feedback arc set** problem, we are given a directed graph with edge weights and seek a set of arcs of minimum total weight whose removal makes the graph acyclic. This repo targets large-scale instances with the hybrid interval-based method.

## License

See the `LICENSE` file in the repository (if present). For academic use, please cite the paper or report associated with this method (if any) and this repository.
