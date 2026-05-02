
"""
This file shows how it is possible to run the environment by itself without the main game code.    
"""

import pygame
import random
from environment import TowerDefenseEnv

env = TowerDefenseEnv(render_mode="rgb_array")

obs, info = env.reset()

terminated = False
truncated = False

seed = random.randint(0, 9999999)
print(f"Using seed: {seed}")

env.action_space.seed(seed)

while not (terminated or truncated):
    action = env.action_space.sample()
    
    obs, reward, terminated, truncated, info, game_state = env.step(action)

print(f"Game ended by: {game_state}")

print()

env.close()
pygame.quit()
