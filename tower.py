
import pygame
import math

class Tower:
    sprite = None
    sprite_size = None
    
    def __init__(self, x: float, y: float, health: int, tile_size: int):

        self.x = x
        self.y = y
        self.health = health
        
        # Load and scale sprite
        if Tower.sprite is None:
            try:
                original = pygame.image.load("Sprites/Towers/Tower-#1.png")
                # Scale to fit tile size
                scale_factor = max(1, tile_size // original.get_width())
                new_size = original.get_width() * scale_factor
                Tower.sprite = pygame.transform.scale(original, (new_size, new_size))
                Tower.sprite_size = new_size
            except pygame.error as e:
                print(f"Could not load tower sprite: {e}")
                Tower.sprite = None
    
    def draw(self, surface: pygame.Surface):

        if Tower.sprite is not None:
            # Draw sprite
            rect = Tower.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(Tower.sprite, rect)
        else:
            # Draw a rectangle if sprite failed to load
            pygame.draw.rect(surface, (100, 100, 100), 
                           (int(self.x - 15), int(self.y - 15), 30, 30))
