"""Run the full comparison and store the raw results."""

import json
import os
import statistics
import time

from . import aco, config, dp, ga, pso
from .instance import generate_instance, load_instance


def _mean_std(values):
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.stdev(values)


def _summarise(rows, algorithms):
    """Build one summary row per algorithm from the raw run rows."""
    out = []
    for algo in algorithms:
        costs = [r["best_cost"] for r in rows if r["algorithm"] == algo]
        times = [r["time"] for r in rows if r["algorithm"] == algo]
        mean, std = _mean_std(costs)
        out.append({
            "algorithm": algo,
            "runs": len(costs),
            "best": min(costs),
            "worst": max(costs),
            "mean": mean,
            "std": std,
            "mean_time": statistics.mean(times),
        })
    return out


def run_experiment(project_root, runs=None, budget=None, verbose=True):
    runs = runs or config.RUNS
    budget = budget or config.EVAL_BUDGET
    data_dir = os.path.join(project_root, "data")
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)

    rows = []
    convergence = {}
    instances = {}
    exact = {}

    for name, n_customers, seed in config.INSTANCES:
        path = os.path.join(data_dir, name + ".csv")
        if os.path.exists(path):
            inst = load_instance(name, path)
        else:
            inst = generate_instance(name, n_customers, seed, path)
        instances[name] = inst
        if verbose:
            print("\n=== instance %s (%d customers) ===" % (name, n_customers))

        if name == "small":
            res = dp.solve(inst)
            exact[name] = res
            rows.append({
                "instance": name, "algorithm": "DP", "run": 0,
                "best_cost": res["best_cost"], "time": res["time"],
                "evals": res["evals"], "best_tour": "-".join(map(str, res["best_tour"])),
            })
            if verbose:
                print("DP   cost %.2f  time %.3fs" % (res["best_cost"], res["time"]))

        histories = {"GA": [], "PSO": [], "ACO": []}
        for run in range(1, runs + 1):
            seed_run = 1000 * run + n_customers

            t0 = time.perf_counter()
            res = ga.solve(inst, budget, config.GA_POP, config.GA_TOURNAMENT,
                           config.GA_CROSSOVER, config.GA_MUTATION,
                           config.GA_ELITE, seed_run)
            histories["GA"].append(res["history"])
            rows.append({
                "instance": name, "algorithm": "GA", "run": run,
                "best_cost": res["best_cost"], "time": res["time"],
                "evals": res["evals"], "best_tour": "-".join(map(str, res["best_tour"])),
                "best_iter": int(min(range(len(res["history"])),
                                     key=lambda i: res["history"][i])),
            })
            if verbose:
                print("GA   run %2d  cost %8.2f  time %6.2fs" %
                      (run, res["best_cost"], time.perf_counter() - t0))

            t0 = time.perf_counter()
            res = pso.solve(inst, budget, config.PSO_SWARM, config.PSO_W_START,
                            config.PSO_W_END, config.PSO_C1, config.PSO_C2,
                            seed_run)
            histories["PSO"].append(res["history"])
            rows.append({
                "instance": name, "algorithm": "PSO", "run": run,
                "best_cost": res["best_cost"], "time": res["time"],
                "evals": res["evals"], "best_tour": "-".join(map(str, res["best_tour"])),
                "best_iter": int(min(range(len(res["history"])),
                                     key=lambda i: res["history"][i])),
            })
            if verbose:
                print("PSO  run %2d  cost %8.2f  time %6.2fs" %
                      (run, res["best_cost"], time.perf_counter() - t0))

            t0 = time.perf_counter()
            res = aco.solve(inst, budget, config.ACO_ANTS, config.ACO_ALPHA,
                            config.ACO_BETA, config.ACO_RHO, config.ACO_Q,
                            seed_run)
            histories["ACO"].append(res["history"])
            rows.append({
                "instance": name, "algorithm": "ACO", "run": run,
                "best_cost": res["best_cost"], "time": res["time"],
                "evals": res["evals"], "best_tour": "-".join(map(str, res["best_tour"])),
                "best_iter": int(min(range(len(res["history"])),
                                     key=lambda i: res["history"][i])),
            })
            if verbose:
                print("ACO  run %2d  cost %8.2f  time %6.2fs" %
                      (run, res["best_cost"], time.perf_counter() - t0))

        # average convergence curve, cut to the shortest history
        cur = {}
        for algo in ("GA", "PSO", "ACO"):
            hs = histories[algo]
            length = min(len(h) for h in hs)
            means = []
            stds = []
            for i in range(length):
                vals = [h[i] for h in hs]
                m, s = _mean_std(vals)
                means.append(m)
                stds.append(s)
            cur[algo] = {"mean": means, "std": stds}
        convergence[name] = cur

    # summaries and gaps
    with open(os.path.join(results_dir, "results.csv"), "w", newline="",
              encoding="utf-8") as f:
        fields = ["instance", "algorithm", "run", "best_cost", "time",
                  "evals", "best_iter", "best_tour", "gap_percent"]
        f.write(",".join(fields) + "\n")
        for r in rows:
            inst_name = r["instance"]
            if inst_name in exact:
                ref = exact[inst_name]["best_cost"]
            else:
                ref = min(x["best_cost"] for x in rows
                          if x["instance"] == inst_name)
            gap = 100.0 * (r["best_cost"] - ref) / ref
            r["gap_percent"] = gap
            f.write("%s,%s,%s,%.6f,%.4f,%d,%s,%s,%.4f\n" % (
                r["instance"], r["algorithm"], r["run"], r["best_cost"],
                r["time"], r["evals"], r.get("best_iter", ""),
                r["best_tour"], gap))

    summary = {}
    for name, _, _ in config.INSTANCES:
        inst_rows = [r for r in rows if r["instance"] == name]
        summary[name] = _summarise(inst_rows, ["GA", "PSO", "ACO"])

    with open(os.path.join(results_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary,
                   "exact": {k: {"cost": v["best_cost"], "time": v["time"],
                                 "tour": v["best_tour"]}
                             for k, v in exact.items()},
                   "budget": budget, "runs": runs}, f, indent=2)
    with open(os.path.join(results_dir, "convergence.json"), "w",
              encoding="utf-8") as f:
        json.dump(convergence, f)

    return rows, summary, exact, convergence, instances
