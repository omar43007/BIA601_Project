"""Particle Swarm Optimization for the TSP using swap sequences.

Each particle is a permutation of the customers and its velocity is a list
of swaps. The difference between two permutations is expressed as the swaps
that turn the first one into the second one.
"""

import random
import time


def difference(a, b):
    """Return a swap sequence that transforms permutation a into b."""
    a = a[:]
    pos = {v: i for i, v in enumerate(a)}
    seq = []
    for i in range(len(a)):
        if a[i] != b[i]:
            j = pos[b[i]]
            a[i], a[j] = a[j], a[i]
            pos[a[i]] = i
            pos[a[j]] = j
            seq.append((i, j))
    return seq


def apply_swaps(tour, seq):
    t = tour[:]
    for i, j in seq:
        t[i], t[j] = t[j], t[i]
    return t


def keep(seq, prob, rng):
    """Multiply a swap sequence by a coefficient by keeping each swap with
    the given probability."""
    if prob >= 1.0:
        return seq[:]
    return [s for s in seq if rng.random() < prob]


def solve(inst, budget, swarm, w_start, w_end, c1, c2, seed):
    rng = random.Random(seed)
    start = time.perf_counter()
    customers = inst.customers
    n = len(customers)
    evals = 0
    history = []

    positions = []
    velocities = []
    for _ in range(swarm):
        t = customers[:]
        rng.shuffle(t)
        positions.append(t)
        velocities.append([(rng.randrange(n), rng.randrange(n))
                           for _ in range(rng.randint(1, max(1, n // 4)))])
    costs = [inst.tour_length(t) for t in positions]
    evals += swarm

    pbest = [t[:] for t in positions]
    pbest_cost = costs[:]
    g = min(range(swarm), key=lambda i: costs[i])
    gbest = positions[g][:]
    gbest_cost = costs[g]
    history.append(gbest_cost)

    iteration = 0
    while evals < budget:
        iteration += 1
        # inertia weight decreases linearly
        progress = min(1.0, evals / budget)
        w = w_start + (w_end - w_start) * progress
        for i in range(swarm):
            seq = keep(velocities[i], w, rng)
            seq += keep(difference(positions[i], pbest[i]), c1 * rng.random(), rng)
            seq += keep(difference(positions[i], gbest), c2 * rng.random(), rng)
            # a velocity longer than n is unnecessary and slows the search
            if len(seq) > n:
                seq = seq[:n]
            velocities[i] = seq
            positions[i] = apply_swaps(positions[i], seq)
            cost = inst.tour_length(positions[i])
            evals += 1
            if cost < pbest_cost[i]:
                pbest_cost[i] = cost
                pbest[i] = positions[i][:]
            if cost < gbest_cost:
                gbest_cost = cost
                gbest = positions[i][:]
            if evals >= budget:
                break
        history.append(gbest_cost)

    elapsed = time.perf_counter() - start
    return {
        "algorithm": "PSO",
        "best_cost": gbest_cost,
        "best_tour": gbest,
        "history": history,
        "evals": evals,
        "time": elapsed,
        "iterations": iteration,
    }
