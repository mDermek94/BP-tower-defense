
import pygame
import random
import heapq

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense Map Maker")

clock = pygame.time.Clock()

INF = 10000000

BOARD_MAX_RANDOM = 10000 # Maximum of random value range
WEIGHT_TUNING = 20       # Weight penalty for tiles closer to the edge

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

def swap_vector2(a, b):
    temp = a
    a = b
    b = temp
    
    return a, b


def draw_board(surface: pygame.Surface, board: list, debug: bool = False):
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
                if not debug: # Draw normal board
                    color = tower_tile_color_a if (row + col) % 2 == 0 else tower_tile_color_b
                else: # Show the random values on the board
                    value = (255 / random_max) * board[row][col]
                    color = (value, value, value)
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

    print(f"home base: {home_base}, enemy spawn: {enemy_spawn}")

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
    
    return home_base_coords, enemy_spawn_coords

def make_board(): # Generate an empty board
    board = []
    for i in range(11):
        board_line = []
        for j in range(11):
            if j == 10 or i == 10:
                board_line.append(8)
            else:
                board_line.append(1)
        
        board.append(board_line)
    return board

def make_random_board(): # Generate random weights for the board tiles
    board = []
    
    global random_max
    random_max = 0
    
    for i in range(11):
        board_line = []
        for j in range(11):
            distance_from_center = abs(j - 4.5) + abs(i - 4.5)
            if j == 10 or i == 10:
                base_weight = INF
            else:
                base_weight = random.uniform(0, BOARD_MAX_RANDOM)
                base_weight += WEIGHT_TUNING * distance_from_center
                if base_weight > random_max:
                    random_max = base_weight
            board_line.append(base_weight)
        
        board.append(board_line)

    return board

def save_board(board, home_base, enemy_spawn): # Save the board into a .txt file
    file = open("board_test_random.txt", "w")
    for row in range(11):
        for col in range(11):
            file.write(str(board[row][col]))
            if col <= 9:
                file.write(",")
        file.write("\n")
    file.write(str(home_base[0]) + "," + str(home_base[1]) + "\n")
    file.write(str(enemy_spawn[0]) + "," + str(enemy_spawn[1]))
    file.close()

def random_start(): # Choose random spawn/base coordinates
    start = random.randrange(0, 4)
    
    coords = (0, 0)
    
    if start == 0:
        coords = (0, random.randrange(0, 10))
    elif start == 1:
        coords = (random.randrange(0, 10), 0)
    elif start == 2:
        coords = (9, random.randrange(0, 10))
    elif start == 3:
        coords = (random.randrange(0, 10), 9)
        
    return coords

def choose_random_start_end(): # Choose two random different coordinates for the home_base and enemy_spawn
    start_coords = random_start()
    end_coords = random_start()
    
    while (start_coords == end_coords): end_coords = random_start()

    return start_coords, end_coords

def dijkstra(board, source, target): # Find the lowest weight path from source to target
    dist = []       # Save distance cost to get from source to the target tile
    visited = []    # Keep track of visited tiles
    prev = []       # For each tile save which tile leads to it on the path
    
    minHeap = []
    
    # Initialize the lists
    for row in range(10):
        dist_row = []
        visited_row = []
        prev_row = []
        for col in range(10):
            dist_row.append(INF)
            visited_row.append(False)
            prev_row.append(None)
        dist.append(dist_row)
        visited.append(visited_row)
        prev.append(prev_row)
    
    dist[source[1]][source[0]] = 0 # Set the source distance to 0
    
    heapq.heappush(minHeap, (0, source[0], source[1])) # Add source weight and coordinates to minHeap
        
    while len(minHeap) > 0: # While there are values in the minHeap
        current = heapq.heappop(minHeap) # Get the current minimum weight value from the heap and pop it
        
        # Current x and y coordinates
        x = current[1]
        y = current[2]
        
        if visited[y][x]: # Check if the tile was already visited
            continue
            
        visited[y][x] = True # If not visited mark as visited
        
        if (x, y) == target: # If path reached target, end
            print("Found Path!!")
            break
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Up, down, left and right vectors
    
        for (dx, dy) in directions: # For each neighboring tile
            # Get x and y of the neighboring tile
            nx = x + dx
            ny = y + dy
            
            if nx < 0 or nx >= 10 or ny < 0 or ny >= 10: # Check if the tile is outside the board
                continue
            
            newDist = dist[y][x] + board[ny][nx] # Save new distance based on the neighboring tile's weight
            
            if newDist < dist[ny][nx]: # If the new distance cost is lower
                dist[ny][nx] = newDist # Save new distance cost
                prev[ny][nx] = (x, y)  # Save previous tile's coordinates
                
                heapq.heappush(minHeap, (newDist, nx, ny)) # Add the new tile to the heap
    
    path = []
    current = target
    
    # Save the minimum cost path using prev
    while current is not None:
        path.append(current)
        current = prev[current[1]][current[0]]
        
    return path
        
        

def main():
    pygame.init()
    
    board = []
    random_board = make_random_board()
    board = make_board()
    
    
    home_base, enemy_spawn = choose_random_start_end()

    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)

    running = True
    board_debug = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    save_board(board, home_base, enemy_spawn)
                elif event.key == pygame.K_b:
                    if board_debug == True:
                        board_debug = False
                    elif board_debug == False:
                        board_debug = True
                elif event.key == pygame.K_g:
                        path = dijkstra(random_board, enemy_spawn, home_base)
                        board = make_board()        
                        for coords in path:
                            board[coords[1]][coords[0]] = 0
                elif event.key == pygame.K_t:
                    board = make_board()
                    random_board = make_random_board()
                    home_base, enemy_spawn = choose_random_start_end()
                    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left-mouse button
                if (pygame.mouse.get_pressed(num_buttons=3) == (1, 0 ,0)):
                    click_pos = list(pygame.mouse.get_pos())
                    if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                        map_x = (click_pos[0] - board_x) // tile_size
                        map_y = (click_pos[1] - board_y) // tile_size
                        if map_x < len(board) - 1 and map_y < len(board) - 1:
                            if board[map_y][map_x] == 1:
                                board[map_y][map_x] = 0
                                random_board[map_y][map_x] = 0
                            elif board[map_y][map_x] == 0:
                                board[map_y][map_x] = 1
                                random_board[map_y][map_x] = random.uniform(0, BOARD_MAX_RANDOM)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Board debug - print board x, y and tile type at mouse position
                if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                    map_x = (click_pos[0] - board_x) // tile_size
                    map_y = (click_pos[1] - board_y) // tile_size
                    if map_x < len(board) - 1 and map_y < len(board) - 1:
                        print(f"x: {map_x}, y: {map_y}, {random_board[map_y][map_x]}")
                        if board[map_y][map_x] == 1:
                            tile_type = "tower"
                            print(tile_type)
                        elif board[map_y][map_x] == 0:
                            tile_type = "path"
                            print(tile_type)
                            
        mouse_pos = list(pygame.mouse.get_pos())
            
        screen.fill(bg_color)
        if board_debug:
            draw_board(screen, random_board, debug=True)
        else:
            draw_board(screen, board)
        
        # Highlight the board tile at mouse position
        if (mouse_pos[0] >= board_x and mouse_pos[0] <= board_x + board_size) and (mouse_pos[1] >= board_y and mouse_pos[1] <= board_y + board_size):
            pygame.draw.rect(screen, (255, 0, 0), ((board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size) + 1, (board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size) + 1, tile_size-1, tile_size-1), 2)
        
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
