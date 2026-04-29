
"""
This file shows how it is possible to run the environment by itself without the main game code.    
"""

import pygame
from environment import TowerDefenseEnv

env = TowerDefenseEnv(render_mode="human")

obs, info = env.reset()

while True:
    action = env.action_space.sample()
    
    obs, reward, terminated, game_state, truncated, info = env.step(action)

    if game_state == "quit" or game_state == "defeat" or game_state == "victory":
        print(f"Game ended by: {game_state}")
        break

    if terminated or truncated:
        obs, info = env.reset()


pygame.quit()
