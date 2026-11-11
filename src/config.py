"""Shared experiment settings for the BIA601 project."""

# Total number of candidate solutions evaluated by each algorithm per run.
EVAL_BUDGET = 15000
RUNS = 10

# Genetic Algorithm
GA_POP = 50
GA_TOURNAMENT = 5
GA_CROSSOVER = 0.90
GA_MUTATION = 0.50
GA_ELITE = 2

# Particle Swarm Optimization
PSO_SWARM = 50
PSO_W_START = 0.90
PSO_W_END = 0.40
PSO_C1 = 1.50
PSO_C2 = 1.50

# Ant Colony Optimization
ACO_ANTS = 50
ACO_ALPHA = 1.0
ACO_BETA = 3.0
ACO_RHO = 0.90      # pheromone left after evaporation (residual coefficient)
ACO_Q = 1.0

# Instance definitions: name, number of customers, random seed
INSTANCES = [
    ("small", 10, 101),
    ("medium", 20, 202),
    ("large", 40, 303),
]

FIG_DPI = 150
