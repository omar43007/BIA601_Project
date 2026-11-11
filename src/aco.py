"""Ant Colony Optimization (Ant System) for the TSP."""

import random
import time


def solve(inst, budget, ants, alpha, beta, rho, q, seed):
    rng = random.Random(seed)
    start = time.perf_counter()
    n_nodes = inst.n
    customers = inst.customers
    evals = 0
    history = []

    def nearest_neighbour_tour():
        unvisited = set(customers)
        tour = []
        cur = 0
        while unvisited:
            nxt = min(unvisited, key=lambda j: inst.dist[cur][j])
            tour.append(nxt)
            unvisited.remove(nxt)
            cur = nxt
        return tour

    # The nearest neighbour tour is used once to scale the initial pheromone.
    nn_tour = nearest_neighbour_tour()
    nn_cost = inst.tour_length(nn_tour)
    tau0 = 1.0 / (n_nodes * nn_cost)
    tau = [[tau0] * n_nodes for _ in range(n_nodes)]

    # It also counts as the first evaluated solution of the colony.
    best_tour = nn_tour[:]
    best_cost = nn_cost
    evals = 1
    history.append(best_cost)

    def build_tour():
        tour = []
        unvisited = set(customers)
        cur = 0
        while unvisited:
            denom = 0.0
            weights = []
            for j in unvisited:
                w = (tau[cur][j] ** alpha) * ((1.0 / inst.dist[cur][j]) ** beta)
                weights.append((j, w))
                denom += w
            r = rng.random() * denom
            acc = 0.0
            chosen = None
            for j, w in weights:
                acc += w
                if acc >= r:
                    chosen = j
                    break
            if chosen is None:
                chosen = weights[-1][0]
            tour.append(chosen)
            unvisited.remove(chosen)
            cur = chosen
        return tour

    def deposit(tour, amount):
        prev = 0
        for node in tour:
            tau[prev][node] += amount
            tau[node][prev] += amount
            prev = node
        tau[prev][0] += amount
        tau[0][prev] += amount

    iteration = 0
    while evals < budget:
        iteration += 1
        tours = []
        for _ in range(ants):
            t = build_tour()
            c = inst.tour_length(t)
            evals += 1
            tours.append((t, c))
            if c < best_cost:
                best_cost = c
                best_tour = t[:]
            if evals >= budget:
                break

        # evaporation (rho is the part of the pheromone that remains)
        for i in range(n_nodes):
            row = tau[i]
            for j in range(n_nodes):
                row[j] *= rho

        for t, c in tours:
            deposit(t, q / c)

        # extra reinforcement of the best route found so far
        deposit(best_tour, q / best_cost)

        history.append(best_cost)

    elapsed = time.perf_counter() - start
    return {
        "algorithm": "ACO",
        "best_cost": best_cost,
        "best_tour": best_tour,
        "history": history,
        "evals": evals,
        "time": elapsed,
        "iterations": iteration,
    }
