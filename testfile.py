
import pygame

pygame.init()

screen_sizes = pygame.display.get_desktop_sizes()

print(screen_sizes)

screen_width = 1920
screen_height = 1080

screen = pygame.display.set_mode(size=(screen_width, screen_height), vsync=1)

pygame.display.set_caption("Tower Defense")

background_color = (0, 255, 0)

clock = pygame.time.Clock()

test_rect = pygame.Rect(screen_width/2 - 25, screen_height/2 - 25, 50, 50)

speed = 5

last_key_vertical = None
last_key_horizontal = None

def draw_board(num_tiles: int, surface: pygame.Surface):
    
    board_x = 0
    board_y = 0
    tile_width = screen_width / num_tiles
    tile_height = screen_height / num_tiles
    
    for i in range(num_tiles):
        for j in range(num_tiles):
            pygame.draw.rect(surface, (0, 0, 0), (board_x, board_y, tile_width, tile_height), 1)
            board_x += tile_width
        board_x = 0
        board_y += tile_height

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'escape':
                    pygame.quit()
                    return
                if event.key in (pygame.K_w, pygame.K_s):
                    last_key_vertical = event.key
                if event.key in (pygame.K_a, pygame.K_d):
                    last_key_horizontal = event.key
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print("Left button")
                elif event.button == 3:
                    print("Right button")

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w] and (last_key_vertical == pygame.K_w or not keys[pygame.K_s]):
            if test_rect.y >= 0:
                test_rect.y -= speed
        if keys[pygame.K_s] and (last_key_vertical == pygame.K_s or not keys[pygame.K_w]):
            if test_rect.y <= screen_height - test_rect.height:
                test_rect.y += speed
        if keys[pygame.K_a] and (last_key_horizontal == pygame.K_a or not keys[pygame.K_d]):
            if test_rect.x >= 0:
                test_rect.x -= speed
        if keys[pygame.K_d] and (last_key_horizontal == pygame.K_d or not keys[pygame.K_a]):
            if test_rect.x <= screen_width - test_rect.width:
                test_rect.x += speed


        screen.fill(background_color)
        
        draw_board(10, screen)
        
        pygame.draw.rect(screen, (255, 0, 0), test_rect)
        
        pygame.display.flip()
                
        clock.tick(60)
    
main()
