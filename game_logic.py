
import pygame
from enemy import Enemy
from tower import Tower
from factory import Factory


def get_tile_center(col, row, board_x, board_y, tile_size):
    cx = board_x + col * tile_size + tile_size / 2
    cy = board_y + row * tile_size + tile_size / 2
    return cx, cy


def draw_tower_inventory(surface, tower_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_panel_color, ui_box_color, ui_box_hover, ui_box_border, mode = 0):

    panel_x = board_x + board_size + 40
    panel_y = board_y
    panel_width = screen_width - panel_x - 10
    panel_height = board_size
    
    if mode == 0:
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
        
        if mode == 0:
            pygame.draw.rect(surface, box_color, box_rect)
            pygame.draw.rect(surface, ui_box_border, box_rect, 2)
        
        if sprite is not None:
            sprite_rect = sprite.get_rect(center=box_rect.center)
            surface.blit(sprite, sprite_rect)
        
        clickable_areas.append((box_rect, i))
    
    return clickable_areas

def draw_factory_inventory(surface, factory_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_box_color, ui_box_hover, ui_box_border, mode = 0):
    panel_x = board_x + board_size + 40
    panel_y = board_y + board_size / 2
    panel_width = screen_width - panel_x - 10
    
    if mode == 0:
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
        
        if mode == 0:
            pygame.draw.rect(surface, box_color, box_rect)
            pygame.draw.rect(surface, ui_box_border, box_rect, 2)
        
        if sprite is not None:
            sprite_rect = sprite.get_rect(center=box_rect.center)
            surface.blit(sprite, sprite_rect)
        
        clickable_areas.append((box_rect, i))
        
    return clickable_areas

def build_enemy_path(board, enemy_spawn, home_base, board_x, board_y, tile_size):
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
                            current_x, current_y = get_tile_center(current[0], current[1], board_x, board_y, tile_size)
                            waypoints.append({"x": current_x, "y": current_y, "dir": dir_name})
                        current = next
                        prev_dir = dir_name
                        break
                    
    current_x, current_y = get_tile_center(goal[0], goal[1], board_x, board_y, tile_size)
    waypoints.append({"x": current_x, "y": current_y, "dir": None})
    
    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn, board_x, board_y, tile_size)
    
    # Adjust first and last waypoints of the path
    if waypoints:
        # 0
        enemy_spawn_x = enemy_spawn_coords[0] + tile_size / 4
        enemy_spawn_y = enemy_spawn_coords[1] + tile_size / 4
        if enemy_spawn[0] == 0: enemy_dir = 'right'
        if enemy_spawn[0] == 9: enemy_dir = 'left'
        if enemy_spawn[1] == 0: enemy_dir = 'down'
        if enemy_spawn[1] == 9: enemy_dir = 'up'
        
        waypoints.insert(0, {"x": enemy_spawn_x, "y": enemy_spawn_y, "dir": enemy_dir})
        
        # -1
        home_base_x = home_base_coords[0] + tile_size / 4
        home_base_y = home_base_coords[1] + tile_size / 4
        
        if home_base[1] == 0: home_dir = 'up'
        if home_base[1] == 9: home_dir = 'down'
        if home_base[0] == 0: home_dir = 'left'
        if home_base[0] == 9: home_dir = 'right'
        
        waypoints[-1]["dir"] = home_dir
        
        waypoints.append({"x": home_base_x, "y": home_base_y, "dir": home_dir})
    
    return waypoints
                

def build_enemy_waves(wave_file):
    waves = []

    with open(wave_file, "r") as file:
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
    
    
def draw_board(surface, board, board_x, board_y, board_size, board_color, tile_count, tile_size, path_tile_color, tower_tile_color_a, tower_tile_color_b, line_color):
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


def get_base_enemy_coords(home_base, enemy_spawn, board_x, board_y, tile_size):
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
    
    #print(home_base_coords, enemy_spawn_coords)
    return home_base_coords, enemy_spawn_coords

def render(board, home_base_coords, enemy_spawn_coords, mouse_pos,
           spawn_started, can_place_towers,
           health, money, resource_1, resource_2,
           current_wave, max_waves, enemy_path,
           tower_sprites, factory_sprites,
           towers, factories, enemies, bullets,
           dragging_tower, dragging_factory, drag_sprite, debug_waypoints,
           screen, bg_color, board_x, board_y, board_size, board_color,
           tile_count, tile_size, path_tile_color, tower_tile_color_a, tower_tile_color_b,
           line_color, play_button_x,
           screen_width, ui_panel_color, ui_box_color, ui_box_hover, ui_box_border):
    

        fonts = {
            "button_font": pygame.font.SysFont(None, 24),
            "money_font": pygame.font.SysFont(None, 26),
            "health_font": pygame.font.SysFont(None, 26),
            "resource_font": pygame.font.SysFont(None, 26),
            "wave_font": pygame.font.SysFont(None, 26)
        }
    
        # Draw background and empty side areas
        screen.fill(bg_color)

        # Draw tiled board
        draw_board(screen, board, board_x, board_y, board_size, board_color, tile_count, tile_size, path_tile_color, tower_tile_color_a, tower_tile_color_b, line_color)

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
            btn_color, btn_label = (200, 160, 40),  "Spawning..."
        elif can_place_towers:
            btn_color, btn_label = (50, 180, 80),   "Play"
        else:
            btn_color, btn_label = (120, 120, 120), "Playing..."
        
        pygame.draw.rect(screen, btn_color, play_btn_rect, border_radius=6)
        pygame.draw.rect(screen, (230, 230, 230), play_btn_rect, 2, border_radius=6)
        label_surf = fonts["button_font"].render(btn_label, True, (0, 0, 0))
        label_rect = label_surf.get_rect(center=play_btn_rect.center)
        screen.blit(label_surf, label_rect)
        # Health HUD
        health_surf = fonts["health_font"].render(f"Health: {health}", True, (230,230,230))
        screen.blit(health_surf, (10, 10))
        
        # Money HUD
        money_surf = fonts["money_font"].render(f"Money: {money}", True, (230, 230, 230))
        screen.blit(money_surf, (10, 35))
        
        # Resource HUD
        resource_1_surf = fonts["resource_font"].render(f"Resource #1: {resource_1}", True, (230, 230, 230))
        screen.blit(resource_1_surf, (10, 60))
        
        resource_2_surf = fonts["resource_font"].render(f"Resource #2: {resource_2}", True, (230, 230, 230))
        screen.blit(resource_2_surf, (10, 85))
        
        # Wave number HUD
        wave_surf = fonts["wave_font"].render(f"Wave: {current_wave}/{max_waves}", True, (230,230,230))
        screen.blit(wave_surf, (play_button_x + 25, board_y + board_size - 25))

        # Debug: draw path waypoints
        if debug_waypoints:
            if enemy_path:
                last_point = None
                for wp in enemy_path:
                    p = (int(wp["x"]), int(wp["y"]))
                    pygame.draw.circle(screen, (0, 255, 255), p, max(2, tile_size // 8))
                    if last_point is not None:
                        pygame.draw.line(screen, (0, 200, 200), last_point, p, 2)
                    last_point = p
        
        # Draw tower inventory panel and get clickable areas
        draw_tower_inventory(screen, tower_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_panel_color, ui_box_color, ui_box_hover, ui_box_border, mode = 0)
        
        draw_factory_inventory(screen, factory_sprites, mouse_pos, board_x, board_y, board_size, screen_width, ui_box_color, ui_box_hover, ui_box_border, mode = 0)

        # Draw all towers
        for tower in towers:
            tower.draw(screen)
        
        # Draw all factories
        for factory in factories:
            factory.draw(screen)
        
        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.draw(screen, size=4)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, size=10)

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

def update_game_state(
    enemies, enemies_spawned, enemies_to_spawn,
    spawn_started, last_spawn_time, spawn_interval,
    enemy_waves, current_wave, MAX_WAVES,
    enemy_path, health,
    towers, factories, bullets,
    board,
    money, resource_1, resource_2,
    can_place_towers,
    factory_death_penalty,
    board_x, board_y, tile_size, screen_width, screen_height, time, time_increment
):
    reward = 0
    game_state = "playing"
    
    # Spawn enemies at time-based intervals
    if spawn_started and enemies_spawned < enemies_to_spawn:
        if time - last_spawn_time >= spawn_interval:
            new_enemy = Enemy(x=0, y=0, type=enemy_waves[current_wave - 1][enemies_spawned])
            new_enemy.set_path(enemy_path)
            enemies.append(new_enemy)
            enemies_spawned += 1
            last_spawn_time = time
            if enemies_spawned == enemies_to_spawn:
                # Finished spawning wave
                spawn_started = False

    # Lock play until wave ends
    if not spawn_started and enemies_spawned == enemies_to_spawn and len(enemies) == 0 and not can_place_towers:
        enemies_spawned = 0
        can_place_towers = True
        current_wave += 1
        if current_wave > MAX_WAVES:
            game_state = "victory"

    delta_time = int(time_increment / 16)
    # Update all enemies and remove those that reached the end
    for enemy in enemies[:]:
        enemy.follow_path(delta_time)
        if enemy.reached_end:
            health -= enemy.damage
            reward -= enemy.damage # Penalize losing health
            enemies.remove(enemy)
        if enemy.type == 2:
            enemy.shoot(time, factories, bullets)
                    
    for tower in towers:
        tower.shoot(time, enemies, bullets)

    for factory in factories[:]:
        production = factory.produce(time, not can_place_towers)
        if factory.type == 0:
            resource_1 += production
            reward += production * 0.2 # Moderate reward for gaining resources
        elif factory.type == 1:
            resource_2 += production
            reward += production * 0.3 # Moderate reward for gaining resources
        if factory.health <= 0:
            # Remove destroyed factories
            factories.remove(factory)
            reward -= factory_death_penalty # Relatively heavy penalty for losing a factory
            # Make board tile available again
            map_x = int((factory.x - board_x) // tile_size)
            map_y = int((factory.y - board_y) // tile_size)
            board[map_y][map_x] = 1

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
                    money += hit_enemy.reward
                    reward += 1 # Reward for defeating enemies
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
    
    if health <= 0:
        reward -= 500 # Heavy penalty for losing
    
    return enemies, enemies_spawned, spawn_started, last_spawn_time, health, money, resource_1, resource_2, current_wave, can_place_towers, reward, game_state

def perform_action(action_type, action_subtype, tile_x, tile_y,
                  board, towers, factories,
                  money, resource_1, resource_2,
                  can_place_towers,
                  enemy_waves, current_wave, 
                  spawn_started, enemies_to_spawn,
                  last_spawn_time,
                  tower0_cost_money,
                  tower1_cost_money, tower1_cost_resource_1,
                  tower2_cost_money, tower2_cost_resource_1, tower2_cost_resource_2,
                  factory0_cost_money,
                  factory1_cost_money, factory1_cost_resource_1,
                  tile_size, board_x, board_y, time):
    
    # Action types:
    #   1: Place tower
    #   2: Place factory
    #   3: Start wave phase
    
    reward = 0
    
    # Can only perform actions during build phase
    if not can_place_towers:
        return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board
    
    # Check if chosen tile is an empty tower tile
    if board[tile_y][tile_x] != 1:
        print("Cannot place building on an occupied tile")
        reward -= 10 # Penalty for trying to build on an occupied tile
        return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board, reward
    
    # Place a tower
    if action_type == 1:
        tower_index = action_subtype
        
        tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
        
        # Tower 0
        if tower_index == 0 and money >= tower0_cost_money:
            new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size)
            money -= tower0_cost_money
            
        # Tower 1
        elif tower_index == 1 and money >= tower1_cost_money and resource_1 >= tower1_cost_resource_1:
            new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=1)
            money -= tower1_cost_money
            resource_1 -= tower1_cost_resource_1
            
        # Tower 2
        elif tower_index == 2 and money >= tower2_cost_money and resource_1 >= tower2_cost_resource_1 and resource_2 >= tower2_cost_resource_2:
            new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size, type=2)
            money -= tower2_cost_money
            resource_1 -= tower2_cost_resource_1
            resource_2 -= tower2_cost_resource_2
            
        else:
            print("Not enough resources to build tower")
            reward -= 10 # Penalty for trying to build without required resources
            return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board, reward
        
        towers.append(new_tower)
        board[tile_y][tile_x] = 2 + new_tower.type
    
    # Place a factory
    elif action_type == 2:
        factory_index = action_subtype
        
        factory_center_x, factory_center_y = get_tile_center(tile_x, tile_y, board_x, board_y, tile_size)
        
        # Factory 0
        if factory_index == 0 and money >= factory0_cost_money:
            new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size)
            money -= factory0_cost_money
        
        # Factory 1
        elif factory_index == 1 and money >= factory1_cost_money and resource_1 >= factory1_cost_resource_1:
            new_factory = Factory(factory_center_x, factory_center_y, health=100, tile_size=tile_size, type=1)
            money -= factory1_cost_money
            resource_1 -= factory1_cost_resource_1
            
        else:
            print("Not enough resources to build factory")
            reward -= 10 # Penalty for trying to build without required resources
            return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board, reward
        
        factories.append(new_factory)
        board[tile_y][tile_x] = 5 + new_factory.type
        
    # Start wave phase
    elif action_type == 3:
        if can_place_towers:
            spawn_started = True
            enemies_to_spawn = len(enemy_waves[current_wave - 1])
            last_spawn_time = time
            can_place_towers = False
        
        return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board, reward
        
    return money, resource_1, resource_2, spawn_started, enemies_to_spawn, last_spawn_time, board, reward

def draw_end_screen(screen, text):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((40, 40, 40, 255))
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    if text == "VICTORY":
        color = (0, 0, 255)
    else:
        color = (255, 0, 0)
    
    screen_x = 100
    screen_y = 100
    
    title = font.render(text, True, color)
    restart_player = small_font.render("Press R to restart", True, (255, 255, 255))
    quit_text = small_font.render("Press ESC to quit", True, (255, 255, 255))
    
    screen.blit(title, (screen_x, screen_y))
    screen.blit(restart_player, (screen_x, screen_y + 100))
    screen.blit(quit_text, (screen_x, screen_y + 200))
    
    pygame.display.flip()

def get_starting_board(board_file):
    board = []
    
    for i in range(11):
        board.append([int(x) for x in board_file.readline().strip().split(",")])
        
    return board
