import gymnasium as gym
import numpy as np
from game_logic import perform_action, update_game_state, get_starting_board

class TowerDefenseEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = gym.spaces.MultiDiscrete([
            4,  # action_type: 0=nothing, 1=build tower, 2=build factory, 3=start wave phase
            3,  # action_subtype: tower/factory type
            10, # x coordinate
            10  # y coordinate
        ])
        
        self.observation_space = gym.spaces.Dict({
            "board": gym.spaces.Box(low=0, high=6, shape=(10, 10), dtype=np.int32),
            "resources": gym.spaces.Box(low=0, high=10000, shape=(5,), dtype=np.int32),
            "next_wave": gym.spaces.Box(low=0, high=1000, shape=(3,), dtype=np.int32)
        })
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        with open(options["board_file"], "r") as f:
            self.board = get_starting_board(f)
        self.money = options["starting_money"]
        self.resource_1 = options["starting_resource_1"]
        self.resource_2 = options["starting_resource_2"]
        self.health = options["starting_health"]
        self.current_wave = 1
        self.enemy_waves = options["enemy_waves"]
        self.max_waves = len(self.enemy_waves)
        
        self.time = 0
        
        self.can_place_towers = True
        
        self.towers = []
        self.factories = []
        self.enemies = []
        self.bullets = []
        
        self.spawn_started = False
        self.last_spawn_time = 0
        self.spawn_interval = 500
        
        self.enemies_to_spawn = len(self.enemy_waves[0])
        self.enemies_spawned = 0
        
        return self.get_obs(), {}
        
    def step(
        self, action,
        tower0_cost_money,
        tower1_cost_money, tower1_cost_resource_1,
        tower2_cost_money, tower2_cost_resource_1, tower2_cost_resource_2,
        factory0_cost_money,
        factory1_cost_money, factory1_cost_resource_1,
        tile_size, factory_death_penalty,
        board_x, board_y, screen_width, screen_height, enemy_path):
        
        action_type, action_subtype, x, y = action
        
        reward = 0
        done = False
        
        self.money, self.resource_1, self.resource_2, \
        self.spawn_started, self.enemies_to_spawn, self.last_spawn_time, self.board = perform_action(
            action_type, action_subtype, x, y,
            self.board, self.towers, self.factories,
            self.money, self.resource_1, self.resource_2,
            self.can_place_towers, self.enemy_waves, self.current_wave,
            False, 0, 0,
            tower0_cost_money,
            tower1_cost_money, tower1_cost_resource_1,
            tower2_cost_money, tower2_cost_resource_1, tower2_cost_resource_2,
            factory0_cost_money,
            factory1_cost_money, factory1_cost_resource_1,
            tile_size, board_x, board_y
        )
        
        self.time += 1
        
        if action_type == 3:
            self.spawn_started = True
            self.enemies_to_spawn = len(self.enemy_waves[self.current_wave - 1])
            self.last_spawn_time = self.time
            self.can_place_towers = False
            
        
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
            reward
        ) = update_game_state(
            self.enemies, self.enemies_spawned, self.enemies_to_spawn,
            self.spawn_started, self.last_spawn_time, self.spawn_interval,
            self.enemy_waves, self.current_wave, self.max_waves,
            enemy_path, self.health,
            self.towers, self.factories, self.bullets, self.board,
            self.money, self.resource_1, self.resource_2, self.can_place_towers,
            factory_death_penalty, board_x, board_y, tile_size, screen_width, screen_height, self.time)
                
            
        if self.health <= 0:
            done = True
        
        if self.current_wave > self.max_waves:
            done = True
            
        return self.get_obs(), reward, done, False, {}
    
    def get_obs(self):
        next_wave = self.enemy_waves[self.current_wave - 1]
        
        counts = [0, 0, 0]
        for enemy in next_wave:
            counts[enemy] += 1
            
        return {
            "board": np.array(self.board, dtype=np.int32),
            "resources": np.array([
                self.money,
                self.resource_1,
                self.resource_2,
                self.health,
                self.current_wave
            ], dtype=np.int32),
            "next_wave": np.array(counts, dtype=np.int32)
        }
