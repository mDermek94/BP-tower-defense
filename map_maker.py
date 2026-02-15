
import pygame

print("Hello World")

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense Map Maker")

clock = pygame.time.Clock()


max_board_width = screen_width - 300
max_board_height = screen_height - 40
board_size = min(max_board_width, max_board_height)

tile_count = 10
tile_size = board_size // tile_count
board_size = tile_size * tile_count

board_x = (screen_width - board_size) // 2
board_y = (screen_height - board_size) // 2

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

def get_tile_center(col: int, row: int):
    cx = board_x + col * tile_size + tile_size / 2
    cy = board_y + row * tile_size + tile_size / 2
    return cx, cy

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


def main():
    pygame.init()
    
    board = []
    
    home_base = enemy_spawn = [0, 0]
    
    for i in range(11):
        board_line = []
        for j in range(11):
            if j == 10 or i == 10:
                board_line.append(8)
            else:
                board_line.append(1)
        
        board.append(board_line)

    home_base_coords = None
    enemy_spawn_coords = None

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = list(pygame.mouse.get_pos())
                if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                    map_x = (click_pos[0] - board_x) // tile_size
                    map_y = (click_pos[1] - board_y) // tile_size
                    if map_x < len(board) - 1 and map_y < len(board) - 1:
                        if board[map_y][map_x] == 1:
                            board[map_y][map_x] = 0
                        elif board[map_y][map_x] == 0:
                            board[map_y][map_x] = 1
            elif event.type == pygame.MOUSEBUTTONUP:
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
        
        
            
        screen.fill(bg_color)
        draw_board(screen, board)
        
        if (mouse_pos[0] >= board_x and mouse_pos[0] <= board_x + board_size) and (mouse_pos[1] >= board_y and mouse_pos[1] <= board_y + board_size):
            if board[(mouse_pos[1] - board_y) // tile_size][(mouse_pos[0] - board_x) // tile_size] == 1:
                pygame.draw.rect(screen, (0, 0, 0), (board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size, board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size, tile_size, tile_size))
                pygame.draw.rect(screen, (255, 0, 0), ((board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size) + 1, (board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size) + 1, tile_size-1, tile_size-1))
        
        # Draw a thin border around the board
        pygame.draw.rect(screen, board_color, (board_x, board_y, board_size, board_size), 2)

        # Draw the home base
        if home_base_coords is not None:
            pygame.draw.rect(screen, (255, 255, 255), (home_base_coords[0], home_base_coords[1], tile_size / 2, tile_size / 2))
            pygame.draw.rect(screen, (0, 0, 255), (home_base_coords[0]+1, home_base_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))

        # Draw the enemy spawn
        if enemy_spawn_coords is not None:
            pygame.draw.rect(screen, (255, 255, 255), (enemy_spawn_coords[0], enemy_spawn_coords[1], tile_size / 2, tile_size / 2))
            pygame.draw.rect(screen, (255, 0, 255), (enemy_spawn_coords[0]+1, enemy_spawn_coords[1]+1, tile_size / 2 - 2, tile_size / 2 - 2))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
main()
