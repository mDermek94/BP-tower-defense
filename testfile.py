import pygame
import time
from enemy import Enemy
from tower import Tower

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()


max_board_width = screen_width - 300
max_board_height = screen_height - 40
board_size = min(max_board_width, max_board_height)

# Make sure board_size is divisible by 15 so tiles are integer-sized
tile_count = 10
tile_size = board_size // tile_count
board_size = tile_size * tile_count

board_x = (screen_width - board_size) // 2
board_y = (screen_height - board_size) // 2

# Colors
bg_color = (40, 40, 40)        # window background
board_color = (0, 0, 0)        # board background
ui_panel_color = (60, 60, 60)  # UI panel background
ui_box_color = (80, 80, 80)    # Tower inventory box
ui_box_hover = (100, 100, 100) # Hover color
ui_box_border = (200, 200, 200) # Border color
line_color = (0, 0, 0)         # grid lines
tower_tile_color_a = (72, 209, 56)
tower_tile_color_b = (42, 115, 33)
path_tile_color = (227, 189, 0)



def get_tile_center(col: int, row: int):
    cx = board_x + col * tile_size + tile_size / 2
    cy = board_y + row * tile_size + tile_size / 2
    return cx, cy


def draw_tower_inventory(surface: pygame.Surface, tower_sprites: list, mouse_pos: tuple):

    panel_x = board_x + board_size + 20
    panel_y = board_y
    panel_width = screen_width - panel_x - 20
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


def build_enemy_path(board: list, enemy_spawn: list, home_base: list):

    total_rows = len(board)
    total_cols = len(board[0]) if total_rows else 0
    
    rows_p = total_rows - 1
    cols_p = total_cols - 1 if total_rows else 0
    if rows_p <= 0 or cols_p <= 0:
        return []

    
    start_x, start_y = int(enemy_spawn[0]), int(enemy_spawn[1])
    end_x, end_y = int(home_base[0]), int(home_base[1])


    current_tile = (start_y, start_x)
    visited_tiles = set([current_tile])

    def neighbors(rc):
        row, col = rc
        for dy, dx, dname in ((0, 1, "right"), (1, 0, "down"), (0, -1, "left"), (-1, 0, "up")):
            new_row, new_col = row + dy, col + dx
            if 0 <= new_row < rows_p and 0 <= new_col < cols_p and board[new_row][new_col] == 0 and (new_row, new_col) not in visited_tiles:
                yield (new_row, new_col, dy, dx, dname)

    initial = None
    for new_row, new_col, dy, dx, dname in neighbors(current_tile):
        initial = (dy, dx, dname)
        break
    if initial is None:
        return []

    dy, dx, dname = initial
    prev = None
    waypoints = []

    scx, scy = get_tile_center(current_tile[1], current_tile[0])
    waypoints.append({"x": scx, "y": scy, "dir": dname})


    while True:
        new_row, new_col = current_tile[0] + dy, current_tile[1] + dx
        can_forward = 0 <= new_row < rows_p and 0 <= new_col < cols_p and board[new_row][new_col] == 0 and (new_row, new_col) != prev and (new_row, new_col) not in visited_tiles

        if can_forward:
            prev = current_tile
            current_tile = (new_row, new_col)
            visited_tiles.add(current_tile)

            if current_tile == (end_y, end_x):
                current_x, current_y = get_tile_center(current_tile[1], current_tile[0])
                waypoints.append({"x": current_x, "y": current_y, "dir": None})
                break
            continue


        turn_found = None
        for turn_row, turn_col, turn_dy, turn_dx, turn_dname in neighbors(current_tile):
            if (turn_row, turn_col) != prev and (turn_dy, turn_dx) != (dy, dx):
                turn_found = (turn_dy, turn_dx, turn_dname)
                break

        current_x, current_y = get_tile_center(current_tile[1], current_tile[0])
        next_dir_name = turn_found[2] if turn_found else None
        waypoints.append({"x": current_x, "y": current_y, "dir": next_dir_name})

        if turn_found is None:
            break

        dy, dx, dname = turn_found
        prev = current_tile
        current_tile = (current_tile[0] + dy, current_tile[1] + dx)
        visited_tiles.add(current_tile)


    return waypoints


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
    elif enemy_spawn[0] == 0:
        enemy_spawn_x = board_x + tile_size * int(enemy_spawn[0]) + tile_size / 4
        enemy_spawn_y = board_y + tile_size * int(enemy_spawn[1]) - tile_size / 2
    elif enemy_spawn[0] == 9:
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
    
    board_file = open("board_test.txt", "r")
    
    board = []
    
    for i in range(11):
        board.append([int(x) for x in board_file.readline().strip().split(",")])
    
    home_base = board_file.readline().strip().split(",")
    enemy_spawn = board_file.readline().strip().split(",")
        
    for i in range(len(home_base)):
        home_base[i] = int(home_base[i])
        enemy_spawn[i] = int(enemy_spawn[i])

    # Build enemy path
    enemy_path = build_enemy_path(board, enemy_spawn, home_base)
    
    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)

    # Adjust first and last waypoints
    if enemy_path:
        enemy_path[0]["x"] = enemy_spawn_coords[0] + tile_size / 4
        enemy_path[0]["y"] = enemy_spawn_coords[1] + tile_size / 4
        
        enemy_path[-1]["x"] = home_base_coords[0] + tile_size / 4
        enemy_path[-1]["y"] = home_base_coords[1] + tile_size / 4

    # Enemies list
    enemies = []
    
    enemies_to_spawn = 5
    enemies_spawned = 0
    spawn_interval = 1.0
    last_spawn_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds

    tower_sprites = []
    try:
        tower_sprite_1 = pygame.image.load("Sprites/Towers/Tower-#1.png")
        # Scale sprite
        tower_sprite_1 = pygame.transform.scale(tower_sprite_1, (60, 60))
        tower_sprites.append(tower_sprite_1)
    except pygame.error as e:
        print(f"Could not load tower sprite: {e}")
        tower_sprites.append(None)

    # Towers list
    towers = []
    
    dragging_tower = False
    dragged_tower_index = None
    drag_sprite = None

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
                
                # Check if clicked on tower inventory to start dragging
                if 'inventory_areas' in locals() and not dragging_tower:
                    for box_rect, tower_index in inventory_areas:
                        if box_rect.collidepoint(click_pos):
                            dragging_tower = True
                            dragged_tower_index = tower_index
                            if tower_index < len(tower_sprites) and tower_sprites[tower_index] is not None:
                                original = pygame.image.load("Sprites/Towers/Tower-#1.png")
                                drag_sprite = pygame.transform.scale(original, (tile_size, tile_size))
                            print(f"Started dragging tower {tower_index}")
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
                            if board[tile_y][tile_x] == 1:
                                # Place tower
                                tower_center_x, tower_center_y = get_tile_center(tile_x, tile_y)
                                new_tower = Tower(tower_center_x, tower_center_y, health=100, tile_size=tile_size)
                                towers.append(new_tower)
                                # Mark tile as occupied
                                board[tile_y][tile_x] = 2
                                print(f"Placed tower at tile ({tile_x}, {tile_y})")
                            else:
                                print(f"Cannot place tower on tile ({tile_x}, {tile_y}) - invalid tile type")
                    
                    # Reset drag state
                    dragging_tower = False
                    dragged_tower_index = None
                    drag_sprite = None
                
                # Board debug
                if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                    map_x = (click_pos[0] - board_x) // tile_size
                    map_y = (click_pos[1] - board_y) // tile_size
                    if map_x < len(board) - 1 and map_y < len(board) - 1:
                        print(f"x: {map_x}, y: {map_y}")
                        if board[map_y][map_x] == 1:
                            tile_type = "tower"
                            print(tile_type)
                        elif board[map_y][map_x] == 0:
                            tile_type = "path"
                            print(tile_type)

        mouse_pos = list(pygame.mouse.get_pos())

        # Spawn enemies at time-based intervals
        current_time = pygame.time.get_ticks() / 1000.0
        if enemies_spawned < enemies_to_spawn:
            if current_time - last_spawn_time >= spawn_interval:
                new_enemy = Enemy(x=0, y=0, health=100, velocity=2.0)
                new_enemy.set_path(enemy_path)
                enemies.append(new_enemy)
                enemies_spawned += 1
                last_spawn_time = current_time

        # Update all enemies and remove those that reached the end
        for enemy in enemies[:]:
            enemy.follow_path()
            if enemy.reached_end:
                enemies.remove(enemy)

        # Draw background and empty side areas
        screen.fill(bg_color)

        # Draw tiled board
        draw_board(screen, board)
        
        if (mouse_pos[0] >= board_x and mouse_pos[0] <= board_x + board_size) and (mouse_pos[1] >= board_y and mouse_pos[1] <= board_y + board_size):
            if board[(mouse_pos[1] - board_y) // tile_size][(mouse_pos[0] - board_x) // tile_size] == 1:
                pygame.draw.rect(screen, (0, 0, 0), (board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size, board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size, tile_size, tile_size))
                pygame.draw.rect(screen, (255, 0, 0), ((board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size) + 1, (board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size) + 1, tile_size-1, tile_size-1))

        # Draw a thin border around the board
        pygame.draw.rect(screen, board_color, (board_x, board_y, board_size, board_size), 2)

        # Draw the home base
        pygame.draw.rect(screen, (255, 255, 255), (home_base_coords[0], home_base_coords[1], tile_size / 2, tile_size / 2))
        pygame.draw.rect(screen, (0, 0, 255), (home_base_coords[0]+1, home_base_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))

        # Draw the enemy spawn
        pygame.draw.rect(screen, (255, 255, 255), (enemy_spawn_coords[0], enemy_spawn_coords[1], tile_size / 2, tile_size / 2))
        pygame.draw.rect(screen, (255, 0, 255), (enemy_spawn_coords[0]+1, enemy_spawn_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))

        # Debug: draw path waypoints
        if enemy_path:
            last_point = None
            for wp in enemy_path:
                p = (int(wp["x"]), int(wp["y"]))
                pygame.draw.circle(screen, (0, 255, 255), p, max(2, tile_size // 8))
                if last_point is not None:
                    pygame.draw.line(screen, (0, 200, 200), last_point, p, 2)
                last_point = p

        # Draw tower inventory panel and get clickable areas
        inventory_areas = draw_tower_inventory(screen, tower_sprites, mouse_pos)

        # Draw all towers
        for tower in towers:
            tower.draw(screen)

        # Draw all active enemies
        for enemy in enemies:
            enemy.draw(screen, color=(255, 100, 100), size=10)

        # Draw dragged tower following mouse
        if dragging_tower and drag_sprite is not None:
            drag_x, drag_y = pygame.mouse.get_pos()
            
            # Show placement preview if hovering over board
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
            
            # Draw tower sprite at mouse cursor
            sprite_rect = drag_sprite.get_rect(center=(drag_x, drag_y))
            screen.blit(drag_sprite, sprite_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

main()
