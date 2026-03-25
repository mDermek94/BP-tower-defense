
#import pygame
import random
import math
from dataclasses import dataclass

@dataclass
class EnemyType:
    type: int
    cost: float
    unlock_wave: int
    base_weight: float

ENEMIES = [
    EnemyType(type=0, cost=1.0, unlock_wave=1, base_weight=1.0),
    EnemyType(type=1, cost=3.0, unlock_wave=4, base_weight=0.8)
]

ENEMY_DECAY_RATE = 0.15

# List of available wave archetypes
WAVE_ARCHETYPES = [
    "balanced",     # Balance of low and higher tier enemies
    "swarm",        # Focus on a large number of low tier enemies
    "strong"        # Focus on a semi-large number of high tier enemies
]

ARCHETYPES_MIN_WAVE = 6

MAX_WAVES = 20

BASE_WAVE_BUDGET = 3
WAVE_BUDGET_GROWTH = 1.3
WAVE_SCALING_FACTOR = 1.1

def get_wave_budget(wave: int):
    # Return a difficulty budget for a wave based on wave number
    
    return BASE_WAVE_BUDGET + (wave ** WAVE_SCALING_FACTOR) * WAVE_BUDGET_GROWTH

def pick_archetype(wave: int):
    # Returns a random archetype
    
    # Only apply archetypes from late game phase onward
    if wave < ARCHETYPES_MIN_WAVE:
        return "balanced"
    
    # Probability of each archetype to be picked
    weights = {
        "balanced": 0.4,
        "swarm": 0.3,
        "strong": 0.3
    }
    
    choices = list(weights.keys())
    probabilities = list(weights.values())
    
    return random.choices(choices, probabilities)[0]

def get_enemy_weight(enemy: EnemyType, wave: int):
    # Get the weight cost of the enemy type for the current wave
    
    # Check if the enmy type can spawn
    if wave < enemy.unlock_wave:
        return 0.0
    
    # Weaker enemies decay faster over time, meaning lower tier enemies are progressively less likely to spawn
    decay = math.exp(-ENEMY_DECAY_RATE * (wave - enemy.unlock_wave))
    
    return enemy.base_weight * decay
    
def apply_archetype_weights(weights: dict, archetype: str):
    # Apply the picked archetype weight modifiers to the enemy weights
    
    modified_weights = weights.copy()
    
    if archetype == "swarm":
        modified_weights[1] *= 2.0 # Boost spawn rate of tier 1 enemies during swarm waves
        
    elif archetype == "strong":
        max_tier = max(modified_weights.keys())
        modified_weights[max_tier] *= 2.0 # Boost spawn rate of highest tier enemies during strong waves
        
    elif archetype == "balanced":
        pass    # Balanced waves stay the same
    
    return modified_weights

def weighted_enemy_choice(weights: dict):
    total = sum(weights.values())
    if total == 0:
        return None
    
    r = random.uniform(0, total)
    current_weight = 0
    
    for key, weight in weights.items():
        current_weight += weight
        if r <= current_weight:
            return key

def generate_wave(wave: int):
    budget = get_wave_budget(wave)
    
    available_enemies = [e for e in ENEMIES if e.unlock_wave <= wave]
    
    weights = {
        e.type: get_enemy_weight(e, wave)
        for e in available_enemies
    }
    
    archetype = pick_archetype(wave)
    weights = apply_archetype_weights(weights, archetype)
    
    wave_groups = []
    
    while budget > 0:
        enemy_id = weighted_enemy_choice(weights)
        if enemy_id is None:
            break
        
        enemy = next(e for e in ENEMIES if e.type == enemy_id)
        
        if archetype == "swarm":
            group_size = random.randint(5, 10)
        elif archetype == "strong":
            group_size = random.randint(1, 4)
        else:
            group_size = random.randint(2, 6)
            
        total_cost = enemy.cost * group_size
        
        if total_cost > budget:
            break
        
        wave_groups.append((group_size, enemy_id))
        budget -= total_cost
        
    return wave_groups, archetype

def generate_game():
    game_waves = []
    
    for wave in range(1, MAX_WAVES + 1):
        groups, archetype = generate_wave(wave)
        while groups == []:
            groups, archetype = generate_wave(wave)
        game_waves.append({
            "wave": wave,
            "archetype": archetype,
            "groups": groups
        })
    
    return game_waves


def save_into_file(waves: list):
    file = open("wave_test_random.txt", "w")
    
    num_wave = 0
    
    for wave in waves:
        file.write(",".join(f"{n}x{t}" for n, t in wave["groups"]))
        num_wave += 1
        if num_wave < len(waves):
            file.write("\n")
        
    file.close()

def main():
    game = generate_game()
    
    for wave in game:
        print(f"Wave {wave["wave"]} ({wave["archetype"]}): ", end="")
        print(", ".join(f"{n}x{t}" for n, t in wave["groups"]))
        
    save_into_file(game)



main()
