
import pygame
import random
import heapq
import argparse

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense Map Maker")

clock = pygame.time.Clock()

INF = 10000000

MAX_MAP_GENERATION_ATTEMPTS = 500

MIN_SOURCE_TARGET_DISTANCE = 2

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
                    if value > 255: value = 255 # Clamp value to black if it somehow gets too high
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

    #print(f"home base: {home_base}, enemy spawn: {enemy_spawn}")

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
    
    # Reverse for correct use in the path_with_waypoints function, which expects points ordered [source -> waypoint -> ... -> waypoint -> target]
    path.reverse()
    return path

def path_with_waypoints(board, source, target, waypoints):
    # Reuse the dijkstra function for finding the shortest path between two points to add several waypoints the path is forced to pass through
    
    full_path = []
    
    # Get a list of points including the source, target and all waypoints
    points = [source] + waypoints + [target]
    
    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        
        # Get a path segment using two points and the dijkstra function
        path_segment = dijkstra(board, start, end)
        
        # Skip duplicate points where the segments connect (since the end point of a previous segment is going to be the same as the start point of its next segment)
        if i > 0:
            path_segment = path_segment[1:]
            
        full_path.extend(path_segment)
        
        for (x, y) in path_segment[1:-1]:
            board[y][x] += INF/2
                
    return full_path

def generate_waypoints_path(source, target, num_waypoints, offset_strength = 2):
    # Generates semi-evenly spaced waypoints between source and target
    
    waypoints = []
    
    sx, sy = source
    ex, ey = target
    
    for i in range(1, num_waypoints + 1):
        # Try to keep even spacing
        t = i / (num_waypoints + 1)
        
        # Base point along a straight line from source to target
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        
        # Perpendicular direction
        dx = ex - sx
        dy = ey - sy
        
        perp_x = -dy
        perp_y = dx
        
        # Normalize
        length = max((perp_x**2 + perp_y**2) ** 0.5, 0.0001) # Avoid division by zero
        perp_x /= length
        perp_y /= length
        
        # Random offset - offsets the point from the line 
        offset = random.uniform(-offset_strength, offset_strength)
        
        x += perp_x * offset
        y += perp_y * offset
        
        # Clamp to grid
        x = int(round(max(0, min(tile_count - 1, x))))
        y = int(round(max(0, min(tile_count - 1, y))))
        
        waypoints.append((x, y))
    
    return waypoints

def generate_waypoints_global(source, target, num_waypoints = 0):
    # Generate waypoints anywhere on the map
    
    waypoints_set = set()
    
    while len(waypoints_set) < num_waypoints:
        x = random.randint(0, tile_count - 1)
        y = random.randint(0, tile_count - 1)
        waypoints_set.add((x, y))
        
    waypoints = list(waypoints_set)
    
    sx, sy = source
    ex, ey = target
    
    dx = ex - sx
    dy = ey - sy
    
    # Sort result based on source and target position so that the chance of the path overlapping itself or being otherwise invalid is lower
    result = sorted(
        waypoints,
        key=lambda wp: (wp[0] - sx) * dx + (wp[1] - sy) * dy
    )
        
    return result

def generate_waypoints(source, target, num_waypoints = 0, offset_strength = 2, mode = 0):
    # Generate a chosen number of waypoints on the map using one of the two modes
    #   Mode 0 - uses generate_waypoints_global()
    #   Mode 1 - uses generate_waypoints_path()
    
    if mode == 0:
        return generate_waypoints_global(source, target, num_waypoints)
    elif mode == 1:
        return generate_waypoints_path(source, target, num_waypoints, offset_strength)
        

def count_path_neighbors(path_set, x, y):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    count = 0
    
    for dx, dy in directions:
        if (x + dx, y + dy) in path_set:
            count += 1
    
    return count

def validate_path(source, target, path):
    # A valid path starts in the source and ends in the target (no extra tiles) and tiles don't bunch up - each tile has a maximum of 2 neighbors (entrance and exit to the tile)
    path_set = set(path)
    
    for i, (x, y) in enumerate(path):
        neighbors = count_path_neighbors(path_set, x, y)
        
        if source not in path_set or target not in path_set:
            return False
        
        if path[i] == source or path[i] == target:
            # Start and end tiles only have 1 neighbor
            if neighbors != 1:
                return False
            
        else:
            # A normal path tile has 2 neighbors
            if neighbors != 2:
                return False
            
    return True

def validate_source_target(source, target, min_dist, max_dist):
    if max_dist is not None:
        return max_dist >= abs(source[0] - target[0]) + abs(source[1] - target[1]) >= 2
    else:
        return abs(source[0] - target[0]) + abs(source[1] - target[1]) >= 2

def generate_valid_path(board, source, target, num_waypoints = 0, waypoint_offset_strength = 2, waypoint_generation_mode = 0):
    path = path_with_waypoints(board, source, target, generate_waypoints(source, target, num_waypoints, waypoint_offset_strength, waypoint_generation_mode))
    
    if validate_path(source, target, path):
        #print(path)
        return path
        
    return None

def count_free_tiles(board):
    num_free_tiles = 0
    
    for row in board:
        for column in board[row]:
            if board[row][column] == 1:
                num_free_tiles += 1
                
    return num_free_tiles

def generate_parameters(difficulty):
    # Generate map generation parameters based on difficulty level
    
    map_D = min(difficulty, 20)
    t = map_D / 20
    
    use_global = bool(t < 0.5)
        
    min_len = int(20 - t * 18)
    max_len = int(35 - t * 15)
        
    num_waypoints = int(5 - t * 5)
    
    waypoint_offset_strength = int(1 + (1 - t) * 4)
    
    if t < 0.4:
        max_start_end_dist = None
        min_start_end_dist = 10
    else:
        max_start_end_dist = int(20 - t * 12)
        min_start_end_dist = 2
    
    return {
        "use_global": use_global,
        "min_path_length": min_len,
        "max_path_length": max_len,
        "waypoint_count": max(0, num_waypoints),
        "waypoint_offset": waypoint_offset_strength,
        "max_start_end_dist": max_start_end_dist,
        "min_start_end_dist": min_start_end_dist
    }

def validate_seed(seed):
    if seed is None:
        return None
    if not (0 <= seed <= 9999999):
        raise ValueError("Seed must be between 0 and 9999999")
    
    return seed

def main():
    parser = argparse.ArgumentParser(prog="tower-defense-map-maker")
    parser.add_argument("--seed", type=int, help="Seed for randomness")
    parser.add_argument("--difficulty", type=int, required=True, help="Difficulty level <1, 20>")
    
    args = parser.parse_args()
    
    seed = validate_seed(args.seed)
    difficulty = max(min(args.difficulty, 20), 1)
    
    if seed is not None:
        random.seed(seed)
        print(f"Starting map maker | difficulty={difficulty} | seed={seed}")
    else:
        print(f"Starting map maker | difficulty={difficulty}")
    
    hints = [
        "Controls:", # Title
        "Left-Click - toggle a tile between path and empty", # M1
        "Right-Click - switch between selecting a start and end point (only works on edge tiles, clicking a start/end tile swaps them)", # M2
        "T - generates new random start and end positions", # T
        "G - generate a path from the current start to current end (disregards difficulty)", # G
        "C - clear the board", # C
        "X - generate a whole map based on seed and difficulty setting", # X
        "S - save the map into map_test_random.txt", # S
        "B - [DEBUG] show current board weights", # B
        "ESC - close the window" # ESC
    ]
    
    for i in range(10):
        print(hints[i])
    
    run_map_maker(seed, difficulty)
    

def run_map_maker(seed, difficulty):
    pygame.init()
    
    board = []
    random_board = make_random_board()
    board = make_board()
    
    spawn_switcher = True
    
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
                    # Quit the game
                    running = False
                elif event.key == pygame.K_s:
                    # Save board into a .txt
                    save_board(board, home_base, enemy_spawn)
                elif event.key == pygame.K_b:
                    # Show board weights debug
                    board_debug = not board_debug
                elif event.key == pygame.K_g:
                    # Generate path
                    random_board = make_random_board()
                    
                    for i in range(MAX_MAP_GENERATION_ATTEMPTS):
                        path = generate_valid_path(random_board, enemy_spawn, home_base, num_waypoints=4, waypoint_offset_strength=4, waypoint_generation_mode=0)
                        if path is None:
                            #print("Unable to generate map, regenerating map weights")
                            random_board = make_random_board()
                        else:
                            break
                    board = make_board()
                    for coords in path:
                        board[coords[1]][coords[0]] = 0
                elif event.key == pygame.K_c:
                    # Clear the board
                    board = make_board()
                elif event.key == pygame.K_t:
                    # Generate new random start and end positions
                    board = make_board()
                    random_board = make_random_board()
                    home_base, enemy_spawn = choose_random_start_end()
                    while not validate_source_target(home_base, enemy_spawn, 2, None):
                        home_base, enemy_spawn = choose_random_start_end()
                    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)
                elif event.key == pygame.K_x:
                    # Generate path
                    for attempt in range(MAX_MAP_GENERATION_ATTEMPTS):
                        params = generate_parameters(difficulty)
                        random_board = make_random_board()
                        home_base, enemy_spawn = choose_random_start_end()
                        #print(abs(enemy_spawn[0] - home_base[0]) + abs(enemy_spawn[1] - home_base[1]))
                        while not validate_source_target(enemy_spawn, home_base, params["min_start_end_dist"], params["max_start_end_dist"]):
                            home_base, enemy_spawn = choose_random_start_end()
                            
                        path = generate_valid_path(random_board, enemy_spawn, home_base, params["waypoint_count"], params["waypoint_offset"], params["use_global"])
                        if seed is not None:
                            random.seed(seed + attempt)
                        else:
                            random.seed()
                        if path is None:
                            continue
                        elif not validate_path(enemy_spawn, home_base, path):
                            #print("Invalid path")
                            continue
                        elif not (params["min_path_length"] <= len(path) <= params["max_path_length"]):
                            #print("Wrong length")
                            continue
                        else:
                            break
                    
                    home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)
                    board = make_board()
                    for coords in path:
                        board[coords[1]][coords[0]] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = list(pygame.mouse.get_pos())
                # Left-mouse button
                if (pygame.mouse.get_pressed(num_buttons=3) == (1, 0, 0)):
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
                # Right-mouse button
                elif (pygame.mouse.get_pressed(num_buttons=3) == (0, 0, 1)):
                    if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                        map_x = (click_pos[0] - board_x) // tile_size
                        map_y = (click_pos[1] - board_y) // tile_size
                        if map_x < len(board) - 1 and map_y < len(board) - 1:
                            if map_x in (0, 9) or map_y in (0, 9):
                                if (map_x, map_y) == home_base or (map_x, map_y) == enemy_spawn:
                                    temp = home_base
                                    home_base = enemy_spawn
                                    enemy_spawn = temp
                                else:
                                    if spawn_switcher:
                                        home_base = (map_x, map_y)
                                    else:
                                        enemy_spawn = (map_x, map_y)
                                    spawn_switcher = not spawn_switcher
                                counter = 0
                                while not validate_source_target(home_base, enemy_spawn, 2, None):
                                    home_base, enemy_spawn = choose_random_start_end()
                                    if counter == 0:
                                        print("[WARNING] Start and end need to have at least one free tile between them")
                                        counter += 1
                                home_base_coords, enemy_spawn_coords = get_base_enemy_coords(home_base, enemy_spawn)
            elif event.type == pygame.MOUSEBUTTONUP:
                # Board debug - print board x, y and tile type at mouse position
                if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                    map_x = (click_pos[0] - board_x) // tile_size
                    map_y = (click_pos[1] - board_y) // tile_size
                    if map_x < len(board) - 1 and map_y < len(board) - 1:
                        #print(f"x: {map_x}, y: {map_y}, {random_board[map_y][map_x]}")
                        if board[map_y][map_x] == 1:
                            tile_type = "tower"
                            #print(tile_type)
                        elif board[map_y][map_x] == 0:
                            tile_type = "path"
                            #print(tile_type)
                            
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
        
        font = pygame.font.SysFont(None, 24)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
if __name__ == "__main__":
    main()
