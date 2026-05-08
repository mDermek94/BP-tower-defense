
"""
This file shows how it is possible to run the environment by itself without the main game code.    
"""

import pygame
import random
from environment import TowerDefenseEnv

env = TowerDefenseEnv(render_mode="dictionary")

obs, info = env.reset()

terminated = False
truncated = False

seed = random.randint(0, 9999999)
print(f"Using seed: {seed}")

reward_sum = 0
num_steps = 0

max_wave = 0

num_episodes = 50

for _ in range(num_episodes):
    env.action_space.seed(seed + _)
    while not (terminated or truncated):
        action = env.action_space.sample()
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        reward_sum += reward
        num_steps += 1

    max_wave += (info["current_wave"] - 1)
    print(f"Game ended by: {info["game_state"]}")
    env.reset()
    terminated = False
    truncated = False

print(f"Average reward over {num_episodes} episodes: {round(reward_sum/num_steps, 2)}, average max reached wave: {max_wave/num_episodes}")

env.close()
