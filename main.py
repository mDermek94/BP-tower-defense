
import pygame
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from enemy import Enemy
from tower import Tower, Bullet
from factory import Factory


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

ENEMY_SPAWN_INTERVAL = 0.5  # Time interval between enemy spawns

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

DEBUG_WAYPOINTS = False

def get_tile_center(col: int, row: int):
    cx = board_x + col * tile_size + tile_size / 2
    cy = board_y + row * tile_size + tile_size / 2
    return cx, cy


def draw_tower_inventory(surface: pygame.Surface, tower_sprites: list, mouse_pos: tuple):

    panel_x = board_x + board_size + 40
    panel_y = board_y
    panel_width = screen_width - panel_x - 10
    panel_height = board_size
    
    pygame.draw.rect(surface, ui_panel_color, (panel_x, panel_y, panel_width, panel_height))
    
    box_size = 80
    box_padding = 10
    start_y = panel_y + 20
    
    clickable_areas = []
    
    for i, sprite in enumerate(tower_sprites):
        box_y = start_y + i * (box_size + box_padding)
        box_rect = pygame.Rect(panel_x + 10, box_y, box_size, box_size)
        
        is_hover = box_rect.collidepoint(mouse_pos)
        box_color = ui_box_hover if is_hover else ui_box_color
        
        pygame.draw.rect(surface, box_color, box_rect)
        pygame.draw.rect(surface, ui_box_border, box_rect, 2)
        
        if sprite is not None:
            sprite_rect = sprite.get_rect(center=box_rect.center)
            surface.blit(sprite, sprite_rect)
        
        clickable_areas.append((box_rect, i))
    
    return clickable_areas

def draw_factory_inventory(surface: pygame.Surface, factory_sprites: list, mouse_pos: tuple):
    panel_x = board_x + board_size + 40
    panel_y = board_y + board_size / 2
    panel_width = screen_width - panel_x - 10
    
    pygame.draw.line(surface, (100, 100, 100), (panel_x, panel_y), (panel_x + panel_width, panel_y), 3)

    box_size = 80
    box_padding = 10
    start_y = panel_y + 20
    
    clickable_areas = []
    
    for i, sprite in enumerate(factory_sprites):
        box_y = start_y + i * (box_size + box_padding)
        box_rect = pygame.Rect(panel_x + 10, box_y, box_size, box_size)
        
        is_hover = box_rect.collidepoint(mouse_pos)
        box_color = ui_box_hover if is_hover else ui_box_color
        
        pygame.draw.rect(surface, box_color, box_rect)
        pygame.draw.rect(surface, ui_box_border, box_rect, 2)
        
        if sprite is not None:
            sprite_rect = sprite.get_rect(center=box_rect.center)
            surface.blit(sprite, sprite_rect)
        
        clickable_areas.append((box_rect, i))
        
    return clickable_areas

def build_enemy_path(board: list, enemy_spawn: list, home_base: list):
    current = (enemy_spawn[0], enemy_spawn[1])
    goal = (home_base[0], home_base[1])
    
    waypoints = []
    directions = ((0, -1, "up"), (-1, 0, "left"), (0, 1, "down"), (1, 0, "right"))
    visited = []
    prev_dir = None
    
    while (current != goal):
        for dir in directions:
            next = (current[0] + dir[0], current[1] + dir[1])
            dir_name = dir[2]
            if (next[0] >= 0 and next[0] <= 9 and next[1] >= 0 and next[1] <= 9):
                if board[next[1]][next[0]] == 0:
                    if next not in visited:
                        visited.append(current)                       
                        if prev_dir != dir_name:
                            current_x, current_y = get_tile_center(current[0], current[1])
                            waypoints.append({"x": current_x, "y": current_y, "dir": dir_name})
                        current = next
                        prev_dir = dir_name
                        break
                    
    current_x, current_y = get_tile_center(goal[0], goal[1])
    waypoints.append({"x": current_x, "y": current_y, "dir": None})
    
    #print("Waypoints:", waypoints)
    return waypoints
                

def build_enemy_waves():
    waves = []

    with open(CURRENT_WAVE_FILE, "r") as file:
        for line in file:
            line = line.strip().split(",")
            
            if line == "":
                break
            
            enemies_in_wave = []
            for num_enemy_type in line:
                enemies_in_wave.append(num_enemy_type.split("x"))
            
            enemies = []
            for i in range(len(enemies_in_wave)):
                for j in range(int(enemies_in_wave[i][0])):
                    if (enemies_in_wave[i][0] != 0):
                        enemies.append(int(enemies_in_wave[i][1]))
            
            if enemies != []:
                waves.append(enemies)

    return waves
    
    
def draw_board(surface: pygame.Surface, board: list):
    # Draw board background
    board_rect = pygame.Rect(board_x, board_y, board_size, board_size)
    pygame.draw.rect(surface, board_color, board_rect)

    # Draw tiles
    for row in range(tile_count):
        for col in range(tile_count):
            x = board_x + col * tile_size
            y = board_y + row * tile_size
            rect = pygame.Rect(x, y, tile_size, tile_size)
            if board[row][col] == 0:
                color = path_tile_color    
            else:
                color = tower_tile_color_a if (row + col) % 2 == 0 else tower_tile_color_b
            pygame.draw.rect(surface, color, rect)

    # Draw grid lines on top
    for i in range(tile_count + 1):

        x = board_x + i * tile_size
        pygame.draw.line(surface, line_color, (x, board_y), (x, board_y + board_size), 1)

        y = board_y + i * tile_size
        pygame.draw.line(surface, line_color, (board_x, y), (board_x + board_size, y), 1)


def get_base_enemy_coords(home_base, enemy_spawn):
    home_base_coords = []
    enemy_spawn_coords = []

    home_base_x = 0
    home_base_y = 0

    if home_base[0] == 0:
        home_base_x = board_x + tile_size * int(home_base[0]) - tile_size / 2
        home_base_y = board_y + tile_size * int(home_base[1]) + tile_size / 4
    elif home_base[0] == 9:
        home_base_x = board_x + tile_size * int(home_base[0]) + tile_size
        home_base_y = board_y + tile_size * int(home_base[1]) + tile_size / 4
    elif home_base[1] == 0:
        home_base_x = board_x + tile_size * int(home_base[0]) + tile_size / 4
        home_base_y = board_y + tile_size * int(home_base[1]) - tile_size / 2
    elif home_base[1] == 9:
        home_base_x = board_x + tile_size * int(home_base[0]) + tile_size / 4
        home_base_y = board_y + tile_size * int(home_base[1]) + tile_size
        
    enemy_spawn_x = 0
    enemy_spawn_y = 0
    
    if enemy_spawn[0] == 0:
        enemy_spawn_x = board_x + tile_size * int(enemy_spawn[0]) - tile_size / 2
        enemy_spawn_y = board_y + tile_size * int(enemy_spawn[1]) + tile_size / 4
    elif enemy_spawn[0] == 9:
        enemy_spawn_x = board_x + tile_size * int(enemy_spawn[0]) + tile_size
        enemy_spawn_y = board_y + tile_size * int(enemy_spawn[1]) + tile_size / 4
    elif enemy_spawn[1] == 0:
        enemy_spawn_x = board_x + tile_size * int(enemy_spawn[0]) + tile_size / 4
        enemy_spawn_y = board_y + tile_size * int(enemy_spawn[1]) - tile_size / 2
    elif enemy_spawn[1] == 9:
        enemy_spawn_x = board_x + tile_size * int(enemy_spawn[0]) + tile_size / 4
        enemy_spawn_y = board_y + tile_size * int(enemy_spawn[1]) + tile_size
        
    home_base_coords.append(home_base_x)
    home_base_coords.append(home_base_y)
    
    enemy_spawn_coords.append(enemy_spawn_x)
    enemy_spawn_coords.append(enemy_spawn_y)
    
    print(home_base_coords, enemy_spawn_coords)
    return home_base_coords, enemy_spawn_coords


def main():
    pygame.init()
    
    board_file = open(CURRENT_BOARD_FILE, "r")
    
    board = []
    
    money = STARTING_MONEY
    health = STARTING_HEALTH
    resource_1 = STARTING_RESOURCE_1
    resource_2 = STARTING_RESOURCE_2
    
    current_wave = 1
    
    for i in range(11):
        board.append([int(x) for x in board_file.readline().strip().split(",")])
    
    for i in range(len(board)):
        print(board[i])
    
    home_base = board_file.readline().strip().split(",")
    enemy_spawn = board_file.readline().strip().split(",")
        
    for i in range(len(home_base)):
        home_base[i] = int(home_base[i])
        enemy_spawn[i] = int(enemy_spawn[i])

    # Build enemy path
    enemy_path = build_enemy_path(board, enemy_spawn, home_base)
        
    enemy_waves = build_enemy_waves()
    MAX_WAVES = len(enemy_waves)
    
    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)

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
    can_spawn = True
    enemies_spawned = 0
    spawn_interval = ENEMY_SPAWN_INTERVAL
    last_spawn_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
    spawn_started = False  # Start spawning only after clicking Play

    # UI fonts
    button_font = pygame.font.SysFont(None, 24)
    money_font = pygame.font.SysFont(None, 26)
    health_font = pygame.font.SysFont(None, 26)
    resource_font = pygame.font.SysFont(None, 26)
    wave_font = pygame.font.SysFont(None, 26)

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
    while running:
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
                if play_btn_rect.collidepoint(click_pos) and can_spawn:
                    # Start or restart the 5-enemy spawn sequence
                    can_spawn = False
                    spawn_started = True
                    enemies_to_spawn = len(enemy_waves[current_wave - 1])
                    print(f"Current wave has {enemies_to_spawn} enemies.")
                    last_spawn_time = pygame.time.get_ticks() / 1000.0
                    can_place_towers = False  # Lock tower placement during wave
                    for factory in factories:
                        factory.last_production_time_ms = current_time
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
                                tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y)
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
                                tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y)
                                new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=tower_index)
                                money -= TOWER1_COST_MONEY
                                resource_1 -= TOWER1_COST_RESOURCE_1
                                towers.append(new_tower)
                                # Mark tile as occupied
                                board[tile_y][tile_x] = 2
                                print(f"Placed tower at tile ({tile_x}, {tile_y})")
                            elif board[tile_y][tile_x] == 1 and money >= TOWER2_COST_MONEY and resource_1 >= TOWER2_COST_RESOURCE_1 and resource_2 >= TOWER2_COST_RESOURCE_2 and tower_index == 2:
                                # Place tower 2
                                tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y)
                                new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=tower_index)
                                money -= TOWER2_COST_MONEY
                                resource_1 -= TOWER2_COST_RESOURCE_1
                                resource_2 -= TOWER2_COST_RESOURCE_2
                                towers.append(new_tower)
                                # Mark tile as occupied
                                board[tile_y][tile_x] = 2
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
                                factory_center_x, factory_center_y = get_tile_center(tile_x, tile_y)
                                new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size)
                                money -= FACTORY0_COST_MONEY
                                factories.append(new_factory)
                                board[tile_y][tile_x] = 2
                                print(f"Placed factory at tile ({tile_x}, {tile_y})")
                            elif (money < FACTORY0_COST_MONEY and factory_index == 0) or (money < FACTORY1_COST_MONEY and factory_index == 1):
                                print(f"Not enough money to place factory. Money: {money}")
                            # Place factory 1
                            elif board[tile_y][tile_x] == 1 and money >= FACTORY1_COST_MONEY and resource_1 >= FACTORY1_COST_RESOURCE_1 and factory_index == 1:
                                factory_center_x, factory_center_y = get_tile_center(tile_x, tile_y)
                                new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size, type=1)
                                money -= FACTORY1_COST_MONEY
                                resource_1 -= FACTORY1_COST_RESOURCE_1
                                factories.append(new_factory)
                                board[tile_y][tile_x] = 2
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
                        print(f"x: {map_x}, y: {map_y}, {get_tile_center(map_x, map_y)}")
                        if board[map_y][map_x] == 1:
                            tile_type = "tower"
                            print(tile_type)
                        elif board[map_y][map_x] == 0:
                            tile_type = "path"
                            print(tile_type)

        mouse_pos = list(pygame.mouse.get_pos())

        # Spawn enemies at time-based intervals
        current_time = pygame.time.get_ticks() / 1000.0
        if spawn_started and enemies_spawned < enemies_to_spawn:
            if current_time - last_spawn_time >= spawn_interval:
                new_enemy = Enemy(x=0, y=0, type=enemy_waves[current_wave - 1][enemies_spawned])
                new_enemy.set_path(enemy_path)
                enemies.append(new_enemy)
                enemies_spawned += 1
                last_spawn_time = current_time
                if enemies_spawned == enemies_to_spawn:
                    # Finished spawning wave
                    spawn_started = False

        # Lock play until wave ends
        if not spawn_started and enemies_spawned == enemies_to_spawn and len(enemies) == 0:
            can_spawn = True
            enemies_spawned = 0
            can_place_towers = True
            if current_wave + 1 <= MAX_WAVES:
                current_wave += 1

        # Update all enemies and remove those that reached the end
        for enemy in enemies[:]:
            enemy.follow_path()
            if enemy.reached_end:
                health -= enemy.damage
                enemies.remove(enemy)

        # Draw background and empty side areas
        screen.fill(bg_color)

        # Draw tiled board
        draw_board(screen, board)

        # Draw a thin border around the board
        pygame.draw.rect(screen, board_color, (board_x, board_y, board_size, board_size), 2)

        # Draw the home base
        pygame.draw.rect(screen, (255, 255, 255), (home_base_coords[0], home_base_coords[1], tile_size / 2, tile_size / 2))
        pygame.draw.rect(screen, (0, 0, 255), (home_base_coords[0]+1, home_base_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))

        # Draw the enemy spawn
        pygame.draw.rect(screen, (255, 255, 255), (enemy_spawn_coords[0], enemy_spawn_coords[1], tile_size / 2, tile_size / 2))
        pygame.draw.rect(screen, (255, 0, 255), (enemy_spawn_coords[0]+1, enemy_spawn_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))

        # Highlight the board tile at mouse position if it is a tower tile
        if (mouse_pos[0] >= board_x and mouse_pos[0] <= board_x + board_size) and (mouse_pos[1] >= board_y and mouse_pos[1] <= board_y + board_size):
            if board[(mouse_pos[1] - board_y) // tile_size][(mouse_pos[0] - board_x) // tile_size] == 1:
                pygame.draw.rect(screen, (255, 0, 0), ((board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size) + 1, (board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size) + 1, tile_size-1, tile_size-1), 2)

        # Draw Play button
        play_btn_rect = pygame.Rect(play_button_x, board_y + board_size + 6, 120, 32)
    
        # Determine button state/color/label
        if spawn_started:
            btn_color, btn_label = (200, 160, 40), "Spawning..."
        elif can_spawn:
            btn_color, btn_label = (50, 180, 80), "Play"
        else:
            btn_color, btn_label = (120, 120, 120), "Playing..."
        
        pygame.draw.rect(screen, btn_color, play_btn_rect, border_radius=6)
        pygame.draw.rect(screen, (230, 230, 230), play_btn_rect, 2, border_radius=6)
        label_surf = button_font.render(btn_label, True, (0, 0, 0))
        label_rect = label_surf.get_rect(center=play_btn_rect.center)
        screen.blit(label_surf, label_rect)
        # Health HUD
        health_surf = health_font.render(f"Health: {health}", True, (230,230,230))
        screen.blit(health_surf, (10, 10))
        
        # Money HUD
        money_surf = money_font.render(f"Money: {money}", True, (230, 230, 230))
        screen.blit(money_surf, (10, 35))
        
        # Resource HUD
        resource_1_surf = resource_font.render(f"Resource #1: {resource_1}", True, (230, 230, 230))
        screen.blit(resource_1_surf, (10, 60))
        
        resource_2_surf = resource_font.render(f"Resource #2: {resource_2}", True, (230, 230, 230))
        screen.blit(resource_2_surf, (10, 85))
        
        # Wave number HUD
        wave_surf = wave_font.render(f"Wave: {current_wave}/{MAX_WAVES}", True, (230,230,230))
        screen.blit(wave_surf, (play_button_x + 25, board_y + board_size - 25))

        # Debug: draw path waypoints
        if DEBUG_WAYPOINTS:
            if enemy_path:
                last_point = None
                for wp in enemy_path:
                    p = (int(wp["x"]), int(wp["y"]))
                    pygame.draw.circle(screen, (0, 255, 255), p, max(2, tile_size // 8))
                    if last_point is not None:
                        pygame.draw.line(screen, (0, 200, 200), last_point, p, 2)
                    last_point = p

        # Draw tower inventory panel and get clickable areas
        tower_inventory_areas = draw_tower_inventory(screen, tower_sprites, mouse_pos)
        
        factory_inventory_areas = draw_factory_inventory(screen, factory_sprites, mouse_pos)

        # Draw all towers (pass milliseconds for cooldown timing)
        # Perform tower actions
        current_time_ms = pygame.time.get_ticks()
        for tower in towers:
            tower.update(current_time_ms, enemies, bullets, screen) # Draw + shoot
        
        # Draw all factories
        # Perform factory actions
        for factory in factories:
            if factory.type == 0:
                resource_1 += factory.produce(current_time_ms, not can_place_towers)
            elif factory.type == 1:
                resource_2 += factory.produce(current_time_ms, not can_place_towers)
            if factory.health <= 0:
                # Remove destroyed factories
                factories.remove(factory)
                # Make board tile available again
                map_x = int((factory.x - board_x) // tile_size)
                map_y = int((factory.y - board_y) // tile_size)
                board[map_y][map_x] = 1
            else:
                factory.draw(screen)
        
        # Update and draw bullets
        delta_time = clock.get_time() / 16.67  # Normalize to ~60fps
        for bullet in bullets[:]:
            bullet.move(delta_time)

            # Build bullet rect
            bullet_size = 4
            bullet_rect = pygame.Rect(int(bullet.x - bullet_size / 2), int(bullet.y - bullet_size / 2), bullet_size, bullet_size)

            if not bullet.is_enemy_bullet:
                # Check enemy hit
                hit_enemy = None
                for enemy in enemies:
                    # Enemy bounding box
                    enemy_radius = getattr(enemy, 'size', 10)
                    enemy_rect = pygame.Rect(int(enemy.x - enemy_radius), int(enemy.y - enemy_radius), enemy_radius * 2, enemy_radius * 2)
                    if bullet_rect.colliderect(enemy_rect):
                        hit_enemy = enemy
                        break

                # Remove bullet and hit enemy and add resource
                if hit_enemy:
                    if hit_enemy.type <= bullet.type:
                        money += getattr(hit_enemy, 'reward', 1)
                        enemies.remove(hit_enemy)
                    bullets.remove(bullet)
                    continue
                
            else:
                # Check factory hit
                hit_factory = None
                for factory in factories:
                    factory_rect = pygame.Rect(int(factory.x - 20), int(factory.y - 20), 40, 40)
                    if bullet_rect.colliderect(factory_rect):
                        hit_factory = factory
                        break
                        
                if hit_factory:
                    factory.health -= bullet.factory_damage
                    bullets.remove(bullet)
                    continue

            # Remove bullets that leave the screen
            if (bullet.x < 0 or bullet.x > screen_width or bullet.y < 0 or bullet.y > screen_height) or can_place_towers:
                bullets.remove(bullet)
                continue

            bullet.draw(screen, size=bullet_size)

        # Draw enemies
        for enemy in enemies:
            enemy.update(current_time_ms, factories, bullets, screen, size=10)

        # Draw tower following mouse
        if (dragging_tower or dragging_factory) and drag_sprite is not None:
            drag_x, drag_y = pygame.mouse.get_pos()
            
            # Show placement preview
            if (drag_x >= board_x and drag_x <= board_x + board_size) and (drag_y >= board_y and drag_y <= board_y + board_size):
                hover_tile_x = (drag_x - board_x) // tile_size
                hover_tile_y = (drag_y - board_y) // tile_size
                
                # Check if valid placement
                if hover_tile_x < len(board[0]) - 1 and hover_tile_y < len(board) - 1:
                    can_place = board[hover_tile_y][hover_tile_x] == 1
                    
                    # Draw highlight on tile
                    tile_screen_x = board_x + hover_tile_x * tile_size
                    tile_screen_y = board_y + hover_tile_y * tile_size
                    
                    # Green if valid, red if invalid
                    overlay_color = (0, 255, 0) if can_place else (255, 0, 0)
                    overlay_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    overlay_surf.fill(overlay_color)
                    screen.blit(overlay_surf, (tile_screen_x, tile_screen_y))
            
            # Draw tower
            sprite_rect = drag_sprite.get_rect(center=(drag_x, drag_y))
            screen.blit(drag_sprite, sprite_rect)

        # Victory - beating all waves
        #if current_wave >= MAX_WAVES:
        #    print("Game finished.")

        # Loss - losing all health
        #if health <= 0:
        #    print("Game lost.")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

main()
