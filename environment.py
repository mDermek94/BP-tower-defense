
import gymnasium as gym
import numpy as np
import pygame
from config import TILE_SIZE, TILE_COUNT, BOARD_X, BOARD_Y, SCREEN_HEIGHT, SCREEN_WIDTH, CURRENT_BOARD_FILE, BOARD_SIZE,\
    STARTING_HEALTH, STARTING_MONEY, STARTING_RESOURCE_1, STARTING_RESOURCE_2,\
    ENEMY_WAVES, ENEMY_PATH, ENEMY_SPAWN_COORDS, HOME_BASE_COORDS, PLAY_BUTTON_X,\
    TOWER0_COST_MONEY, TOWER1_COST_MONEY, TOWER1_COST_RESOURCE_1, TOWER2_COST_MONEY, TOWER2_COST_RESOURCE_1, TOWER2_COST_RESOURCE_2,\
    FACTORY0_COST_MONEY, FACTORY1_COST_MONEY, FACTORY1_COST_RESOURCE_1, FACTORY_DEATH_PENALTY,\
    TOWER_SPRITES, FACTORY_SPRITES, BOARD, BG_COLOR, BOARD_COLOR, LINE_COLOR, UI_BOX_COLOR, UI_PANEL_COLOR, PATH_TILE_COLOR, TOWER_TILE_COLOR_A, TOWER_TILE_COLOR_B, UI_BOX_BORDER, UI_BOX_HOVER
from game_logic import perform_action, update_game_state, get_starting_board, render

class TowerDefenseEnv(gym.Env):
    metadata = {
        "render_modes": ["dictionary", "human"],
        "render_fps": 60,
    }
    
    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode

        self.action_space = gym.spaces.MultiDiscrete([
            3,  # action_type: 0=build tower, 1=build factory, 2=start wave phase
            3,  # action_subtype: tower/factory type
            10, # x coordinate
            10  # y coordinate
        ])
        
        # Observation space
        self.observation_space = gym.spaces.Dict({
            "board": gym.spaces.Box(low=0, high=6, shape=(10, 10), dtype=np.int32),         # The state of the game grid - what towers and factories are where and where is the path enemies walk on
            "resources": gym.spaces.Box(low=0, high=100000, shape=(5,), dtype=np.int32),    # Health, Money, Resource_1, Resouce_2, current wave index
            "next_wave": gym.spaces.Box(low=0, high=10000, shape=(3,), dtype=np.int32),      # How many enemies of each type there are in the next wave, example 1 type0, 2 type1 and 4 type2 enemies are represented as [1, 2, 4]
            "next_3_waves": gym.spaces.Box(low=0, high=10000, shape=(3, 3), dtype=np.int32)  # Show the next three waves to further allow the agent to plan ahead
        })
        
        self.window = None
        self.clock = None
        
        self.board = None
        self.money = None
        self.resource_1 = None
        self.resource_2 = None
        self.health = None
        self.current_wave = None
        self.enemy_waves = None
        self.max_waves = None
        self.game_state = "playing"
        
        self.time = 0
        self.can_place_towers = True
        self.towers = []
        self.factories = []
        self.enemies = []
        self.bullets = []
        self.wave_reward = 0
        self.spawn_started = False
        self.last_spawn_time = 0
        self.spawn_interval = 500
        self.enemies_to_spawn = 0
        self.enemies_spawned = 0
    
    def reset(self, seed=None, options=None):
        # Resets the environment to a base state
        
        super().reset(seed=seed)
        
        # Set all the variables
        with open(CURRENT_BOARD_FILE, "r") as f:
            self.board = get_starting_board(f)
            
        self.money = STARTING_MONEY
        self.resource_1 = STARTING_RESOURCE_1
        self.resource_2 = STARTING_RESOURCE_2
        self.health = STARTING_HEALTH
        self.current_wave = 1
        self.enemy_waves = ENEMY_WAVES
        self.max_waves = len(self.enemy_waves)
        
        self.time = 0
        self.can_place_towers = True
        self.towers = []
        self.factories = []
        self.enemies = []
        self.bullets = []
        self.wave_reward = 0
        self.game_state = "playing"
        
        self.spawn_started = False
        self.last_spawn_time = 0
        self.spawn_interval = 500
        self.time_increment = 16
        self.enemies_to_spawn = len(self.enemy_waves[0])
        self.enemies_spawned = 0
        
        obs = self._get_obs()
        info = self._get_info()
        return obs, info
        
    def step(self, action):
        
        action_type, action_subtype, x, y = action # Get the agent action
        
        was_in_wave = not self.can_place_towers    # Phase transition detection
        
        done = False    # Terminated
        
        self.game_state = "playing"
        
        if self.can_place_towers:
            # If in build phase, perform an action based on [action_type, action_subtype, x, y]
            self.money, self.resource_1, self.resource_2, \
            self.spawn_started, self.enemies_to_spawn, self.last_spawn_time, self.board, reward = perform_action(
                action_type, action_subtype, x, y,
                self.board, self.towers, self.factories,
                self.money, self.resource_1, self.resource_2,
                self.can_place_towers, self.enemy_waves, self.current_wave,
                False, 0, 0,
                TOWER0_COST_MONEY,
                TOWER1_COST_MONEY, TOWER1_COST_RESOURCE_1,
                TOWER2_COST_MONEY, TOWER2_COST_RESOURCE_1, TOWER2_COST_RESOURCE_2,
                FACTORY0_COST_MONEY,
                FACTORY1_COST_MONEY, FACTORY1_COST_RESOURCE_1,
                TILE_SIZE, BOARD_X, BOARD_Y, self.time
            )
            
            self.wave_reward += reward
            
            if action_type == 2: # Action = swap to wave phase
                self.spawn_started = True
                self.enemies_to_spawn = len(self.enemy_waves[self.current_wave - 1])
                self.last_spawn_time = self.time
                self.can_place_towers = False
                # Just return current state, since the agent cannot perform any actions after starting a wave
                return self._get_obs(), self.wave_reward, done, False, self._get_info()
            
            # Update the game state
            (self.enemies,
                self.enemies_spawned,
                self.spawn_started,
                self.last_spawn_time,
                self.health,
                self.money,
                self.resource_1,
                self.resource_2,
                self.current_wave,
                self.can_place_towers,
                reward, self.game_state
            ) = update_game_state(
                self.enemies, self.enemies_spawned, self.enemies_to_spawn,
                self.spawn_started, self.last_spawn_time, self.spawn_interval,
                self.enemy_waves, self.current_wave, self.max_waves,
                ENEMY_PATH, self.health,
                self.towers, self.factories, self.bullets, self.board,
                self.money, self.resource_1, self.resource_2, self.can_place_towers,
                FACTORY_DEATH_PENALTY, BOARD_X, BOARD_Y, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, self.time, self.time_increment)
            
            self.time += self.time_increment 
        
        if not self.can_place_towers:
            # During the wave phase
            
            # Update game state and calculate the reward or penalty
            (self.enemies,
                self.enemies_spawned,
                self.spawn_started,
                self.last_spawn_time,
                self.health,
                self.money,
                self.resource_1,
                self.resource_2,
                self.current_wave,
                self.can_place_towers,
                reward, self.game_state
            ) = update_game_state(
                self.enemies, self.enemies_spawned, self.enemies_to_spawn,
                self.spawn_started, self.last_spawn_time, self.spawn_interval,
                self.enemy_waves, self.current_wave, self.max_waves,
                ENEMY_PATH, self.health,
                self.towers, self.factories, self.bullets, self.board,
                self.money, self.resource_1, self.resource_2, self.can_place_towers,
                FACTORY_DEATH_PENALTY, BOARD_X, BOARD_Y, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, self.time, self.time_increment)
            
            self.time += self.time_increment    # Increment the timer
            self.wave_reward += reward          # Accumulate total reward during the wave
        
        # Print the reward for the last wave
        if was_in_wave and self.can_place_towers:
            print(f"Wave {self.current_wave - 1} finished. Total reward: {round(self.wave_reward, 2)}.")
            self.wave_reward = 0
        
        if self.health <= 0:
            print(f"Wave {self.current_wave} finished. Total reward: {round(self.wave_reward, 2)}.")
            self.game_state = "defeat"
            done = True
        
        if self.current_wave - 1 >= self.max_waves:
            #print(f"Wave {self.current_wave} finished. Total reward: {round(self.wave_reward, 2)}.")
            self.game_state = "victory"
            done = True
        
        if self.render_mode == "human":
            self.render(mode=self.render_mode)
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = "quit"
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "quit"
                        done = True
        
        return self._get_obs(), self.wave_reward, done, False, self._get_info()
    
    def _count_enemy_types(self, wave):
        counts = [0, 0, 0]
        
        for enemy_type in wave:
            if 0 <= enemy_type < 3:
                counts[enemy_type] += 1
                
        return counts
    
    def _get_obs(self):
        # Get the current observation space
        
        if self.current_wave - 1 >= self.max_waves:
            next_wave = []
        else:
            next_wave = self.enemy_waves[self.current_wave - 1] # Adjust next wave
        
        # Calculate enemy counts per type for the next wave
        next_wave_counts = self._count_enemy_types(next_wave)
        
        # Next 3 waves
        next_3_waves = []
        
        for offset in range(3):
            wave_index = self.current_wave - 1 + offset
            if wave_index >= self.max_waves:
                wave_counts = [0, 0, 0]
            else:
                wave_counts = self._count_enemy_types(self.enemy_waves[wave_index])
    
            next_3_waves.append(wave_counts)
        
        # Return the observation
        return {
            "board": np.array([row[:10] for row in self.board[:10]], dtype=np.int32),
            "resources": np.array([
                self.money,
                self.resource_1,
                self.resource_2,
                self.health,
                self.current_wave
            ], dtype=np.int32),
            "next_wave": np.array(next_wave_counts, dtype=np.int32),
            "next_3_waves": np.array(next_3_waves, dtype=np.int32)
        }

    def _get_info(self):
        
        return {
            "game_state": self.game_state,
            "health": self.health,
            "money": self.money,
            "resource_1": self.resource_1,
            "resource_2": self.resource_2,
            "current_wave": self.current_wave
        }
    
    def render(self, mode = "dictionary"):
        if mode not in self.metadata["render_modes"]:
            raise ValueError(f"Unsupported render mode: {mode}")

        img = self._get_obs()

        if mode == "dictionary":
            return img

        if mode == "human":
            self._make_window()
            
            render(BOARD, HOME_BASE_COORDS, ENEMY_SPAWN_COORDS, (-110, -100),
                self.spawn_started, self.can_place_towers,
                self.health, self.money, self.resource_1, self.resource_2,
                self.current_wave, self.max_waves, ENEMY_PATH,
                TOWER_SPRITES, FACTORY_SPRITES,
                self.towers, self.factories, self.enemies, self.bullets,
                False, False, None, False,
                self.window, BG_COLOR, BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_COLOR,
                TILE_COUNT, TILE_SIZE, PATH_TILE_COLOR, TOWER_TILE_COLOR_A, TOWER_TILE_COLOR_B,
                LINE_COLOR, PLAY_BUTTON_X, SCREEN_WIDTH,
                UI_PANEL_COLOR, UI_BOX_COLOR, UI_BOX_HOVER, UI_BOX_BORDER)

            pygame.display.flip()
            if self.clock:
                self.clock.tick(self.metadata["render_fps"])
            
            return None
    
    def _make_window(self):
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Tower Defense Environment")
            self.clock = pygame.time.Clock()
    
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None
