"""Problem instance: a depot and a set of delivery points on a 2-D plane."""

import csv
import math
import os
import random


class Instance:
    """Symmetric TSP instance on Euclidean coordinates.

    Node 0 is the depot. Customers are nodes 1..n-1. A solution is a
    permutation of the customer nodes; the route always starts and ends
    at the depot.
    """

    def __init__(self, name, coords):
        self.name = name
        self.coords = coords
        self.n = len(coords)
        self.dist = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            xi, yi = coords[i]
            for j in range(self.n):
                xj, yj = coords[j]
                self.dist[i][j] = math.hypot(xi - xj, yi - yj)

    @property
    def customers(self):
        return list(range(1, self.n))

    def tour_length(self, tour):
        """Length of a route that starts at the depot, visits tour in order,
        and comes back to the depot."""
        if not tour:
            return 0.0
        total = self.dist[0][tour[0]]
        for a, b in zip(tour, tour[1:]):
            total += self.dist[a][b]
        total += self.dist[tour[-1]][0]
        return total


def generate_instance(name, n_customers, seed, path):
    """Create a reproducible random instance and write it to a CSV file."""
    rng = random.Random(seed)
    coords = [(50.0, 50.0)]  # depot in the middle of the area
    while len(coords) < n_customers + 1:
        x = round(rng.uniform(0.0, 100.0), 2)
        y = round(rng.uniform(0.0, 100.0), 2)
        # avoid points that are almost on top of each other
        if all(math.hypot(x - px, y - py) > 3.0 for px, py in coords):
            coords.append((x, y))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "x", "y"])
        for i, (x, y) in enumerate(coords):
            writer.writerow([i, x, y])
    return Instance(name, coords)


def load_instance(name, path):
    coords = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            coords.append((float(row["x"]), float(row["y"])))
    return Instance(name, coords)
