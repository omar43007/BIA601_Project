"""Exact solution of small TSP instances with the Held-Karp algorithm."""

import time


def solve(inst):
    """Return the optimal tour and its length using bitmask dynamic
    programming. Only suitable for small instances (about 15 customers)."""
    start = time.perf_counter()
    customers = inst.customers
    m = len(customers)
    size = 1 << m
    inf = float("inf")

    dp = [[inf] * m for _ in range(size)]
    parent = [[-1] * m for _ in range(size)]

    for j in range(m):
        dp[1 << j][j] = inst.dist[0][customers[j]]

    for mask in range(size):
        for j in range(m):
            if not (mask & (1 << j)) or dp[mask][j] == inf:
                continue
            base = dp[mask][j]
            cur = customers[j]
            for k in range(m):
                if mask & (1 << k):
                    continue
                nxt = customers[k]
                nm = mask | (1 << k)
                val = base + inst.dist[cur][nxt]
                if val < dp[nm][k]:
                    dp[nm][k] = val
                    parent[nm][k] = j

    full = size - 1
    best_cost = inf
    last = -1
    for j in range(m):
        val = dp[full][j] + inst.dist[customers[j]][0]
        if val < best_cost:
            best_cost = val
            last = j

    # rebuild the tour
    tour = []
    mask = full
    j = last
    while j != -1:
        tour.append(customers[j])
        pj = parent[mask][j]
        mask ^= (1 << j)
        j = pj
    tour.reverse()

    elapsed = time.perf_counter() - start
    return {
        "algorithm": "DP",
        "best_cost": best_cost,
        "best_tour": tour,
        "history": [best_cost],
        "evals": size * m,
        "time": elapsed,
    }
