"""Genetic Algorithm with permutation encoding, order crossover and inversion."""

import random
import time


def order_crossover(p1, p2, rng):
    """Order crossover (OX): copy a segment from p1 and fill the rest in the
    order they appear in p2."""
    n = len(p1)
    a = rng.randrange(n)
    b = rng.randrange(n)
    if a > b:
        a, b = b, a
    if a == b:
        b = min(n, a + 1)
    child = [None] * n
    child[a:b] = p1[a:b]
    used = set(child[a:b])
    fill = [g for g in p2[b:] + p2[:b] if g not in used]
    pos = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill[pos]
            pos += 1
    return child


def inversion_mutation(tour, rng):
    """Reverse a random segment of the tour."""
    n = len(tour)
    a = rng.randrange(n)
    b = rng.randrange(n)
    if a > b:
        a, b = b, a
    if b - a < 2:
        return tour[:]
    return tour[:a] + tour[a:b + 1][::-1] + tour[b + 1:]


def tournament_select(pop, costs, k, rng):
    best = rng.randrange(len(pop))
    for _ in range(k - 1):
        c = rng.randrange(len(pop))
        if costs[c] < costs[best]:
            best = c
    return pop[best]


def solve(inst, budget, pop_size, tournament, crossover_rate, mutation_rate,
          elite, seed):
    """Run the GA until the evaluation budget is used up."""
    rng = random.Random(seed)
    start = time.perf_counter()
    customers = inst.customers
    evals = 0
    history = []

    pop = []
    for _ in range(pop_size):
        t = customers[:]
        rng.shuffle(t)
        pop.append(t)
    costs = [inst.tour_length(t) for t in pop]
    evals += pop_size

    best_idx = min(range(pop_size), key=lambda i: costs[i])
    best_tour = pop[best_idx][:]
    best_cost = costs[best_idx]
    history.append(best_cost)

    generation = 0
    while evals < budget:
        generation += 1
        order = sorted(range(pop_size), key=lambda i: costs[i])
        new_pop = [pop[i][:] for i in order[:elite]]
        new_costs = [costs[i] for i in order[:elite]]

        while len(new_pop) < pop_size:
            p1 = tournament_select(pop, costs, tournament, rng)
            p2 = tournament_select(pop, costs, tournament, rng)
            if rng.random() < crossover_rate:
                child = order_crossover(p1, p2, rng)
            else:
                child = p1[:]
            if rng.random() < mutation_rate:
                child = inversion_mutation(child, rng)
            cost = inst.tour_length(child)
            evals += 1
            new_pop.append(child)
            new_costs.append(cost)
            if cost < best_cost:
                best_cost = cost
                best_tour = child[:]
            if evals >= budget:
                break

        pop, costs = new_pop, new_costs
        history.append(best_cost)

    elapsed = time.perf_counter() - start
    return {
        "algorithm": "GA",
        "best_cost": best_cost,
        "best_tour": best_tour,
        "history": history,
        "evals": evals,
        "time": elapsed,
        "generations": generation,
    }
