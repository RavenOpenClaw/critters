import random
import math
import statistics
import sys
import os

# Add src to path to import constants and MatingHut (if needed)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from constants import (
    BREED_INHERIT_A, BREED_INHERIT_B, BREED_WILDCARD,
    BREED_WILDCARD_LOG_WEIGHT, BREED_WILDCARD_UNIFORM_WEIGHT,
    BREED_WILDCARD_LOG_MU, BREED_WILDCARD_LOG_SIGMA,
    BREED_MUTATION_MIN, BREED_MUTATION_MAX
)

class MockCritter:
    def __init__(self, s, sp, e):
        self.strength = s
        self.speed_stat = sp
        self.endurance = e

def roll_wildcard():
    """Roll a random stat base value using the wildcard distribution."""
    r_type = random.random()
    if r_type < BREED_WILDCARD_UNIFORM_WEIGHT:
        return random.randint(1, 100)
    else:
        val = random.lognormvariate(BREED_WILDCARD_LOG_MU, BREED_WILDCARD_LOG_SIGMA)
        return max(1, min(100, int(val)))

def determine_stat(val1, val2):
    """Determine a single stat value based on inheritance and mutation."""
    r = random.random()
    if r < BREED_INHERIT_A:
        base = val1
    elif r < BREED_INHERIT_A + BREED_INHERIT_B:
        base = val2
    else:
        base = roll_wildcard()
    
    # Apply mutation
    mutation = random.uniform(BREED_MUTATION_MIN, BREED_MUTATION_MAX)
    return max(1, min(100, int(base * mutation)))

def breed(parent1, parent2):
    s = determine_stat(parent1.strength, parent2.strength)
    sp = determine_stat(parent1.speed_stat, parent2.speed_stat)
    e = determine_stat(parent1.endurance, parent2.endurance)
    return (s, sp, e)

def run_simulation(n=1000):
    # Test just the roll_random_stat()
    rolls = [roll_wildcard() for _ in range(n)]
    
    print("=" * 40)
    print("CRITTER BREEDING SIMULATION REPORT")
    print("=" * 40)
    print(f"Analysis of {n} 'Wildcard' rolls:")
    print(f"Average: {statistics.mean(rolls):.2f}")
    print(f"Median: {statistics.median(rolls)}")
    print(f"Mode: {statistics.mode(rolls)}")
    print(f"Max: {max(rolls)}")
    print(f"Count >= 90: {len([s for s in rolls if s >= 90])} ({len([s for s in rolls if s >= 90])/n*100:.2f}%)")
    print(f"Count == 100: {len([s for s in rolls if s >= 100])} ({len([s for s in rolls if s >= 100])/n*100:.2f}%)")
    
    # Frequency distribution
    buckets = [0] * 11
    for s in rolls:
        buckets[min(s // 10, 10)] += 1
    
    print("\nWildcard Distribution (Frequency):")
    for i in range(10):
        bar = '#' * (buckets[i] * 50 // n)
        print(f"{i*10:2d}-{i*10+9:2d}: {bar}")
    print(f"100+:   {'#' * (buckets[10] * 50 // n)}")

    # Breeding test
    p1 = MockCritter(50, 50, 50)
    p2 = MockCritter(50, 50, 50)
    results = [breed(p1, p2) for _ in range(n)]
    str_stats = [r[0] for r in results]
    
    print("-" * 40)
    print(f"Simulation: 1000 offspring from (50, 50, 50) parents:")
    print(f"Average STR: {statistics.mean(str_stats):.2f}")
    print(f"Improvement (> 50): {len([s for s in str_stats if s > 50])} ({len([s for s in str_stats if s > 50])/n*100:.2f}%)")
    print(f"Elite (> 80): {len([s for s in str_stats if s > 80])} ({len([s for s in str_stats if s > 80])/n*100:.2f}%)")
    print(f"Perfect (100): {len([s for s in str_stats if s == 100])} ({len([s for s in str_stats if s == 100])/n*100:.2f}%)")
    print("=" * 40)

if __name__ == "__main__":
    run_simulation(1000)

