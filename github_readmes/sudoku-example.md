# SAT-Based Sudoku Solver

An example of using a **SAT solver** (MiniSat) to solve **Sudoku** in C++. Created as part of a blog series on SAT solvers.

## Reference

- **Blog post:** [Modern SAT solvers: fast, neat, underused (Part 1 of N)](https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/)

## What is in this repo

- C++ code that encodes Sudoku as a SAT instance and solves it with MiniSat.
- Instructions to build and run (compiler, MiniSat library).
- Optional comparison with other solvers (e.g. the one by Aleš Hrabalík linked in the blog).

## How to build and run

1. Install MiniSat (library and headers) and a C++ compiler.
2. Build the project (e.g. make or g++ with -lminisat).
3. Run the executable; optionally pass a puzzle grid (format as in the repo).

## License

See the LICENSE file in the repository. For the SAT series, see the blog link above.
