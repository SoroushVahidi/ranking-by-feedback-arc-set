# Fairness Maximization among Offline Agents in Online Matching Markets

Implementation of parts of the paper on **fairness for offline agents in online matching markets** (greedy and related algorithms).

## Reference

- **Paper (arXiv):** https://arxiv.org/abs/2109.08934  
- This repo implements (subsets of) the algorithms studied in that paper, including the **greedy algorithm for GFM** (Group Fairness Maximization). There may be a gap between the results obtained here and the paper’s reported results; for large random test cases, the average competitive ratio is often close to **(e−1)/e ≈ 0.632**, so in some settings the offline part can be skipped for speed.

## What's in this repo

- Code for the greedy and possibly other algorithms from the paper.
- Experiments or scripts on synthetic or real matching instances.
- Notes on differences from the paper’s figures (if any).

## How to run

1. Clone the repository and install dependencies (e.g. Python or C++, as in the project).
2. Run the main script or executable with the desired instance and parameters.
3. See in-repo docs for input format (e.g. bipartite graph, arrival order).

## License

See the `LICENSE` file in the repository (if present). For academic use, please cite the arXiv paper above and this repository.
