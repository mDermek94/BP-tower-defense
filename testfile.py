
import pygame

# Window size
screen_width = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

# Determine board size (square) and align so left/right sides are empty
# Leave some horizontal room for UI later: subtract 300 from width as empty side space
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
line_color = (0, 0, 0)         # grid lines
tower_tile_color_a = (72, 209, 56)
tower_tile_color_b = (42, 115, 33)
path_tile_color = (227, 189, 0)



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
                if board[row][col] == '0':
                    color = path_tile_color    
                elif board[row][col] == '1':
                    color = tower_tile_color_a if (row + col) % 2 == 0 else tower_tile_color_b
                pygame.draw.rect(surface, color, rect)

        # Draw grid lines on top
        for i in range(tile_count + 1):
            # vertical
            x = board_x + i * tile_size
            pygame.draw.line(surface, line_color, (x, board_y), (x, board_y + board_size), 1)
            # horizontal
            y = board_y + i * tile_size
            pygame.draw.line(surface, line_color, (board_x, y), (board_x + board_size, y), 1)



def main():
    pygame.init()
    
    board_file = open("board_test.txt", "r")
    
    board = []
    
    for i in range(10):
        board.append(board_file.readline().strip().split(","))
            
    print(board_file.readline())

    print(f"Window: {screen_width}x{screen_height}, board_size={board_size}, tile_size={tile_size}")

    running = True
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
                if (click_pos[0] >= board_x and click_pos[0] <= board_x + board_size) and (click_pos[1] >= board_y and click_pos[1] <= board_y + board_size):
                    map_x = (click_pos[0] - board_x) // tile_size
                    map_y = (click_pos[1] - board_y) // tile_size
                    print(f"x: {map_x}, y: {map_y}")
                    if board[map_y][map_x] == '1':
                        print("Tower tile")
                    elif board[map_y][map_x] == '0':
                        print("Path tile")


        mouse_pos = list(pygame.mouse.get_pos())

        # Draw background and empty side areas
        screen.fill(bg_color)

        # Draw tiled board
        draw_board(screen, board)
        
        if (mouse_pos[0] >= board_x and mouse_pos[0] <= board_x + board_size) and (mouse_pos[1] >= board_y and mouse_pos[1] <= board_y + board_size):
            pygame.draw.rect(screen, (0, 0, 0), (board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size, board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size, tile_size, tile_size))
            pygame.draw.rect(screen, (255, 0, 0), ((board_x + ((mouse_pos[0] - board_x) // tile_size) * tile_size) + 1, (board_y + ((mouse_pos[1] - board_y) // tile_size) * tile_size) + 1, tile_size-1, tile_size-1))

        # Draw a thin border around the board
        pygame.draw.rect(screen, board_color, (board_x, board_y, board_size, board_size), 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


main()
