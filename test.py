
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

num_episodes = 100

for _ in range(num_episodes):
    last_wave = [None, None, None]
    current_wave = 0
    
    while not (terminated or truncated):
        action = env.action_space.sample()
        
        obs, reward, terminated, truncated, info, game_state = env.step(action)
        
        current_wave_count = obs["next_wave"]
        if last_wave[0] != current_wave_count[0] or last_wave[1] != current_wave_count[1] or last_wave[2] != current_wave_count[2]:
            current_wave += 1
            last_wave = current_wave_count
        
        
        reward_sum += reward
        num_steps += 1

    max_wave += current_wave
    print(f"Game ended by: {game_state}")
    env.reset()
    terminated = False
    truncated = False

print(f"Average reward over {num_episodes} episodes: {round(reward_sum/num_steps, 2)}, average max reached wave: {max_wave/num_episodes}")

env.close()
pygame.quit()
