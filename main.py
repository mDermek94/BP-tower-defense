
import pygame
from tower import Tower
from factory import Factory
from game_logic import *
from agent_environment import TowerDefenseEnv

use_agent = True

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

max_board_width = screen_width - 300
max_board_height = screen_height - 40
board_size = min(max_board_width, max_board_height)

tile_count = 10
tile_size = board_size // tile_count
board_size = tile_size * tile_count

board_x = (screen_width - board_size) // 2
board_y = (screen_height - board_size) // 2

play_button_x = board_x - 135

# Colors
bg_color = (40, 40, 40)             # Window background
board_color = (0, 0, 0)             # Board background
ui_panel_color = (60, 60, 60)       # UI panel background
ui_box_color = (80, 80, 80)         # Tower inventory box
ui_box_hover = (100, 100, 100)      # Hover color
ui_box_border = (200, 200, 200)     # Border color
line_color = (0, 0, 0)              # Grid lines
tower_tile_color_a = (72, 209, 56)  # Tower tile 1
tower_tile_color_b = (42, 115, 33)  # Tower tile 2
path_tile_color = (227, 189, 0)     # Path tile

CURRENT_BOARD_FILE = "board_test_random.txt"
CURRENT_WAVE_FILE = "wave_test_random.txt"

KILL_REWARD = 1.0           # Money for defeating an enemy
HEALTH_PENALTY = 1.0        # Health lost per enemy reaching the home base

ENEMY_SPAWN_INTERVAL = 500  # Time interval between enemy spawns in ms

# Tower costs
TOWER0_COST_MONEY = 5

TOWER1_COST_MONEY = 5
TOWER1_COST_RESOURCE_1 = 5

TOWER2_COST_MONEY = 10
TOWER2_COST_RESOURCE_1 = 0
TOWER2_COST_RESOURCE_2 = 10

# Factory costs
FACTORY0_COST_MONEY = 5

FACTORY1_COST_MONEY = 10
FACTORY1_COST_RESOURCE_1 = 10

# Starting resources
STARTING_HEALTH = 100

STARTING_MONEY = 100
STARTING_RESOURCE_1 = 100
STARTING_RESOURCE_2 = 100

# Agent reward values
FACTORY_DEATH_PENALTY = 10

DEBUG_WAYPOINTS = False


def main():
    pygame.init()
    
    board_file = open(CURRENT_BOARD_FILE, "r")
    
    board = []
    
    money = STARTING_MONEY
    health = STARTING_HEALTH
    resource_1 = STARTING_RESOURCE_1
    resource_2 = STARTING_RESOURCE_2
    
    current_wave = 1
    
    board = get_starting_board(board_file)
    
    for i in range(len(board)):
        print(board[i])
    
    home_base = board_file.readline().strip().split(",")
    enemy_spawn = board_file.readline().strip().split(",")
        
    for i in range(len(home_base)):
        home_base[i] = int(home_base[i])
        enemy_spawn[i] = int(enemy_spawn[i])

    # Build enemy path
    enemy_path = build_enemy_path(board, enemy_spawn, home_base, board_x, board_y, tile_size)
        
    enemy_waves = build_enemy_waves(CURRENT_WAVE_FILE)
    MAX_WAVES = len(enemy_waves)
    
    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn, board_x, board_y, tile_size)

    # Adjust first and last waypoints of the path
    if enemy_path:
        # 0
        enemy_spawn_x = enemy_spawn_coords[0] + tile_size / 4
        enemy_spawn_y = enemy_spawn_coords[1] + tile_size / 4
        if enemy_spawn[0] == 0: enemy_dir = 'right'
        if enemy_spawn[0] == 9: enemy_dir = 'left'
        if enemy_spawn[1] == 0: enemy_dir = 'down'
        if enemy_spawn[1] == 9: enemy_dir = 'up'
        
        enemy_path.insert(0, {"x": enemy_spawn_x, "y": enemy_spawn_y, "dir": enemy_dir})
        
        # -1
        home_base_x = home_base_coords[0] + tile_size / 4
        home_base_y = home_base_coords[1] + tile_size / 4
        
        if home_base[1] == 0: home_dir = 'up'
        if home_base[1] == 9: home_dir = 'down'
        if home_base[0] == 0: home_dir = 'left'
        if home_base[0] == 9: home_dir = 'right'
        
        enemy_path[-1]["dir"] = home_dir
        
        enemy_path.append({"x": home_base_x, "y": home_base_y, "dir": home_dir})

    bullets = []

    # Enemies list
    enemies = []
    
    enemies_to_spawn = 1
    enemies_spawned = 0
    spawn_interval = ENEMY_SPAWN_INTERVAL
    last_spawn_time = pygame.time.get_ticks()
    spawn_started = False  # Start spawning only after clicking Play

    # UI fonts
    fonts = {
        "button_font": pygame.font.SysFont(None, 24),
        "money_font": pygame.font.SysFont(None, 26),
        "health_font": pygame.font.SysFont(None, 26),
        "resource_font": pygame.font.SysFont(None, 26),
        "wave_font": pygame.font.SysFont(None, 26)
    }

    tower_sprites = []
    try:
        tower_sprite_1 = pygame.image.load("Sprites/Towers/Tower-#1.png")
        # Scale sprite
        tower_sprite_1 = pygame.transform.scale(tower_sprite_1, (60, 60))
        tower_sprites.append(tower_sprite_1)
        
        tower_sprite_2 = pygame.image.load("Sprites/Towers/Tower-#2.png")
        # Scale sprite
        tower_sprite_2 = pygame.transform.scale(tower_sprite_2, (60, 60))
        tower_sprites.append(tower_sprite_2)
        
        tower_sprite_3 = pygame.image.load("Sprites/Towers/Tower-#3.png")
        # Scale sprite
        tower_sprite_3 = pygame.transform.scale(tower_sprite_3, (60, 60))
        tower_sprites.append(tower_sprite_3)
    except pygame.error as e:
        print(f"Could not load tower sprite: {e}")
        tower_sprites.append(None)

    factory_sprites = []
    try:
        factory_sprite_1 = pygame.image.load("Sprites/Factories/Factory-#1.png")
        # Scale sprite
        factory_sprite_1 = pygame.transform.scale(factory_sprite_1, (60, 60))
        factory_sprites.append(factory_sprite_1)
        
        factory_sprite_2 = pygame.image.load("Sprites/Factories/Factory-#2.png")
        # Scale sprite
        factory_sprite_2 = pygame.transform.scale(factory_sprite_2, (60, 60))
        factory_sprites.append(factory_sprite_2)
    except pygame.error as e:
        print(f"Could not load factory sprite: {e}")
        factory_sprites.append(None)

    # Towers list
    towers = []
    
    dragging_tower = False
    drag_sprite = None
    can_place_towers = True  # Locked during an active wave

    factories = []
    
    dragging_factory = False

    running = True
    tile_type = ""
    
    if use_agent:
        env = TowerDefenseEnv()

        obs, _ = env.reset(options={
            "board_file": CURRENT_BOARD_FILE,
            "starting_money": STARTING_MONEY,
            "starting_resource_1": STARTING_RESOURCE_1,
            "starting_resource_2": STARTING_RESOURCE_2,
            "starting_health": STARTING_HEALTH,
            "enemy_waves": enemy_waves
        })
        
        done = False
    
    
    while running:
        mouse_pos = list(pygame.mouse.get_pos())
        if not use_agent:
            tower_inventory_areas = draw_tower_inventory(screen, tower_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_panel_color, ui_box_color, ui_box_hover, ui_box_border, mode=1)
            factory_inventory_areas = draw_factory_inventory(screen, factory_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_box_color, ui_box_hover, ui_box_border, mode=1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Window close
                    running = False
                elif event.type == pygame.KEYDOWN: # On key press
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        print(pygame.key.name(event.key))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = list(pygame.mouse.get_pos())
                    
                    # Play button: bottom-left next to the board
                    play_btn_rect = pygame.Rect(play_button_x, board_y + board_size + 6, 120, 32)
                    if play_btn_rect.collidepoint(click_pos) and can_place_towers:
                        # Start the enemy spawn sequence
                        spawn_started = True
                        enemies_to_spawn = len(enemy_waves[current_wave - 1])
                        print(f"Current wave has {enemies_to_spawn} enemies.")
                        last_spawn_time = pygame.time.get_ticks()
                        can_place_towers = False  # Lock tower placement during wave
                        print("Play pressed: spawning sequence started")
                        continue
                    
                    # Check if clicked on tower inventory to start dragging
                    if 'tower_inventory_areas' in locals() and not dragging_tower and can_place_towers:
                        for box_rect, tower_index in tower_inventory_areas:
                            if box_rect.collidepoint(click_pos):
                                dragging_tower = True
                                if tower_index < len(tower_sprites) and tower_sprites[tower_index] is not None:
                                    original = pygame.image.load(f"Sprites/Towers/Tower-#{tower_index + 1}.png")
                                    drag_sprite = pygame.transform.scale(original, (tile_size, tile_size))
                                print(f"Started dragging tower {tower_index}")
                                break
                            
                    if 'factory_inventory_areas' in locals() and not dragging_factory and can_place_towers:
                        for box_rect, factory_index in factory_inventory_areas:
                            if box_rect.collidepoint(click_pos):
                                dragging_factory = True
                                if factory_index < len(factory_sprites) and factory_sprites[factory_index] is not None:
                                    original = pygame.image.load(f"Sprites/Factories/Factory-#{factory_index + 1}.png")
                                    drag_sprite = pygame.transform.scale(original, (tile_size, tile_size))
                                print(f"Started draggin factory {factory_index}")
                                break
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging_tower:
                        # Try to place tower on board
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Check if mouse is on board
                        if (mouse_x >= board_x and mouse_x <= board_x + board_size) and (mouse_y >= board_y and mouse_y <= board_y + board_size):
                            tile_x = (mouse_x - board_x) // tile_size
                            tile_y = (mouse_y - board_y) // tile_size
                            
                            # Check if tile is valid
                            if tile_x < len(board[0]) - 1 and tile_y < len(board) - 1:
                                # Tower placement
                                if board[tile_y][tile_x] == 1 and money >= TOWER0_COST_MONEY and tower_index == 0:
                                    # Place tower 0
                                    tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
                                    new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size)
                                    money -= TOWER0_COST_MONEY
                                    towers.append(new_tower)
                                    # Mark tile as occupied
                                    board[tile_y][tile_x] = 2
                                    print(f"Placed tower at tile ({tile_x}, {tile_y})")
                                elif (money < TOWER0_COST_MONEY and tower_index == 0) or (money < TOWER1_COST_MONEY and tower_index == 1) or (money < TOWER2_COST_MONEY and tower_index == 2):
                                    print(f"Not enough money to place tower. Money: {money}")
                                elif board[tile_y][tile_x] == 1 and money >= TOWER1_COST_MONEY and resource_1 >= TOWER1_COST_RESOURCE_1 and tower_index == 1:
                                    # Place tower 1
                                    tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
                                    new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=tower_index)
                                    money -= TOWER1_COST_MONEY
                                    resource_1 -= TOWER1_COST_RESOURCE_1
                                    towers.append(new_tower)
                                    # Mark tile as occupied
                                    board[tile_y][tile_x] = 3
                                    print(f"Placed tower at tile ({tile_x}, {tile_y})")
                                elif board[tile_y][tile_x] == 1 and money >= TOWER2_COST_MONEY and resource_1 >= TOWER2_COST_RESOURCE_1 and resource_2 >= TOWER2_COST_RESOURCE_2 and tower_index == 2:
                                    # Place tower 2
                                    tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
                                    new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=tower_index)
                                    money -= TOWER2_COST_MONEY
                                    resource_1 -= TOWER2_COST_RESOURCE_1
                                    resource_2 -= TOWER2_COST_RESOURCE_2
                                    towers.append(new_tower)
                                    # Mark tile as occupied
                                    board[tile_y][tile_x] = 4
                                    print(f"Placed tower at tile ({tile_x}, {tile_y})")
                                elif tower_index == 1 and resource_1 < 5:
                                    print(f"Not enough resource_1 to place tower. Resource_1: {resource_1}")
                                elif tower_index == 2 and resource_2 < 10:
                                    print(f"Not enough resource_1 to place tower. Resource_1: {resource_1}")
                                else:
                                    print(f"Cannot place tower on tile ({tile_x}, {tile_y}) - invalid tile type")
                        
                        # Reset drag state
                        dragging_tower = False
                        drag_sprite = None
                        
                    if dragging_factory:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        if (mouse_x >= board_x and mouse_x <= board_x + board_size) and (mouse_y >= board_y and mouse_y <= board_y + board_size):
                            tile_x = (mouse_x - board_x) // tile_size
                            tile_y = (mouse_y - board_y) // tile_size
                            # Factory placement
                            if tile_x < len(board[0]) - 1 and tile_y < len(board) - 1:
                                # Place factory 0
                                if board[tile_y][tile_x] == 1 and money >= FACTORY0_COST_MONEY and factory_index == 0:
                                    factory_center_x, factory_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
                                    new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size)
                                    money -= FACTORY0_COST_MONEY
                                    factories.append(new_factory)
                                    board[tile_y][tile_x] = 5
                                    print(f"Placed factory at tile ({tile_x}, {tile_y})")
                                elif (money < FACTORY0_COST_MONEY and factory_index == 0) or (money < FACTORY1_COST_MONEY and factory_index == 1):
                                    print(f"Not enough money to place factory. Money: {money}")
                                # Place factory 1
                                elif board[tile_y][tile_x] == 1 and money >= FACTORY1_COST_MONEY and resource_1 >= FACTORY1_COST_RESOURCE_1 and factory_index == 1:
                                    factory_center_x, factory_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
                                    new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size, type=1)
                                    money -= FACTORY1_COST_MONEY
                                    resource_1 -= FACTORY1_COST_RESOURCE_1
                                    factories.append(new_factory)
                                    board[tile_y][tile_x] = 6
                                    print(f"Placed factory at tile ({tile_x}, {tile_y})")
                                elif factory_index == 1 and resource_1 < FACTORY1_COST_RESOURCE_1:
                                    print(f"Not enough resource 1 to place factory. Resource_1: {resource_1}, Cost: {FACTORY1_COST_RESOURCE_1}")
                                else:
                                    print(f"Cannot place factory on tile ({tile_x}, {tile_y}) - invalid tile type")
                        
                        dragging_factory = False
                        drag_sprite = None
                            
                    
                    # Board debug
                    if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                        map_x = (click_pos[0] - board_x) // tile_size
                        map_y = (click_pos[1] - board_y) // tile_size
                        if map_x < len(board) - 1 and map_y < len(board) - 1:
                            print(f"x: {map_x}, y: {map_y}, {get_tile_center(map_x, map_y, board_x, board_y, tile_size)}")
                            if board[map_y][map_x] == 1:
                                tile_type = "tower"
                                print(tile_type)
                            elif board[map_y][map_x] == 0:
                                tile_type = "path"
                                print(tile_type)
                                
            enemies, enemies_spawned, spawn_started, last_spawn_time, health, money, resource_1, resource_2, current_wave, can_place_towers, reward = update_game_state(enemies, enemies_spawned, enemies_to_spawn, spawn_started, last_spawn_time, spawn_interval,
            enemy_waves, current_wave, MAX_WAVES, enemy_path, health, towers, factories, bullets, board,
            money, resource_1, resource_2, can_place_towers, FACTORY_DEATH_PENALTY,
            board_x, board_y, tile_size, screen_width, screen_height, pygame.time.get_ticks())
            
        if use_agent and not done:
            pygame.time.delay(200)
            
            action = env.action_space.sample()
            
            obs, reward, done, truncated, info = env.step(
                action,
                TOWER0_COST_MONEY,
                TOWER1_COST_MONEY, TOWER1_COST_RESOURCE_1,
                TOWER2_COST_MONEY, TOWER2_COST_RESOURCE_1, TOWER2_COST_RESOURCE_2,
                FACTORY0_COST_MONEY,
                FACTORY1_COST_MONEY, FACTORY1_COST_RESOURCE_1,
                tile_size, FACTORY_DEATH_PENALTY,
                board_x, board_y, screen_width, screen_height, enemy_path
            )
            
            board = env.board
            spawn_started = env.spawn_started
            can_place_towers = env.can_place_towers
            health = env.health
            money = env.money
            resource_1 = env.resource_1
            resource_2 = env.resource_2
            current_wave = env.current_wave
            towers = env.towers
            factories = env.factories
            
            print(reward)
            
        
        render(board, home_base_coords, enemy_spawn_coords, mouse_pos,
                   spawn_started, can_place_towers, fonts,
                   health, money, resource_1, resource_2,
                   current_wave, MAX_WAVES, enemy_path,
                   tower_sprites, factory_sprites,
                   towers, factories, enemies, bullets,
                   dragging_tower, dragging_factory, drag_sprite, DEBUG_WAYPOINTS,
                   screen, bg_color, board_x, board_y, board_size, board_color,
                   tile_count, tile_size, path_tile_color, tower_tile_color_a, tower_tile_color_b,
                   line_color, play_button_x, screen_width,
                   ui_panel_color, ui_box_color, ui_box_hover, ui_box_border)
            
        clock.tick(60)

    pygame.quit()

main()
