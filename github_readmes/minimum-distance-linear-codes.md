# Code for Minimum-Distance Linear Codes Problem

This repository contains the **design and implementation of a genetic algorithm** for the **minimum distance of linear codes** problem. It was developed as the final project for an **Artificial Intelligence** course. The implementation is in **C++** and **MiniZinc** (constraint modeling), giving both heuristic (GA) and declarative (MiniZinc) perspectives on the problem.

## Problem

For a linear code with given parameters (e.g. length, dimension), the **minimum distance** is the smallest Hamming distance between any two distinct codewords. Computing or bounding this value is central in coding theory and is known to be hard in general. This project uses a **genetic algorithm** to search for codewords that certify a lower bound on the minimum distance (or to approach the true minimum distance).

## What's in this repo

- **C++** implementation of the genetic algorithm (population, fitness, crossover, mutation, etc.).
- **MiniZinc** models for the same or related formulation (optional comparison or verification).
- Documentation or reports describing the design choices and experimental results (if present in the repo).

## How to build and run

1. **Clone the repository**
   ```bash
   git clone https://github.com/SoroushVahidi/Code-for-minimum-distance-linear-codes-problem.git
   cd Code-for-minimum-distance-linear-codes-problem
   ```

2. **C++**  
   Compile with a C++ compiler (e.g. `g++`). Check for a `Makefile`, `CMakeLists.txt`, or build instructions in the repo. Run the executable with the desired code parameters (e.g. length, dimension).

3. **MiniZinc**  
   If you use MiniZinc, install the [MiniZinc toolchain](https://www.minizinc.org/) and run:
   ```bash
   minizinc model.mzn data.dzn
   ```
   (Use the actual filenames present in the repo.)

## Requirements

- C++ compiler (e.g. g++, clang++).
- MiniZinc (optional, for constraint models).
- Any libraries noted in the project (e.g. for random number generation or linear algebra).

## Citation / context

This work was done as a final project for an AI course. If you build on this code, please acknowledge the repository and the course context.

## License

See the `LICENSE` file in the repository (if present). For academic use, please cite or acknowledge the repo.
