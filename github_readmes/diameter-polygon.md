# Diameter of a Convex Polygon (Parallel Algorithm)

An implementation of the **parallel algorithm for finding the diameter of a convex polygon** as described in **Goodrich’s algorithm book**, written in **C++** with **OpenMP**.

## Reference

- The algorithm (rotating calipers or parallel search) is from the standard textbook by Goodrich et al. This repo provides a parallelized implementation suitable for teaching or benchmarking.

## What's in this repo

- C++ source code using OpenMP for parallelization.
- Logic to compute the diameter (maximum distance between any two vertices) of a convex polygon.
- Instructions or a simple driver to run on sample polygons.

## How to build and run

1. Clone the repo and ensure you have a C++ compiler with OpenMP support (e.g. `g++ -fopenmp`).
2. Compile (e.g. `make` or `g++ -fopenmp -o diameter diameter.cpp`).
3. Run with an input polygon (format as in the repo—e.g. list of points).

## Requirements

- C++ compiler with OpenMP (e.g. GCC, Clang).
- OpenMP runtime (usually included with the compiler).

## License

See the `LICENSE` file in the repository (if present). For academic use, please cite the Goodrich reference and this repository.
