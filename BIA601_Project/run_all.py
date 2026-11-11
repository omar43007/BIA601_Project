"""Entry point: generate instances, run all algorithms, save results and plots.

Usage:
    python run_all.py
    python run_all.py --runs 5 --budget 10000
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import charts, config
from src.experiments import run_experiment


def main():
    parser = argparse.ArgumentParser(description="BIA601 optimization project")
    parser.add_argument("--runs", type=int, default=config.RUNS)
    parser.add_argument("--budget", type=int, default=config.EVAL_BUDGET)
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    rows, summary, exact, convergence, instances = run_experiment(
        root, runs=args.runs, budget=args.budget)

    if not args.no_figures:
        charts.make_all(root, rows, summary, exact, convergence, instances)


if __name__ == "__main__":
    main()
