
import pygame
from math import *
import os

class Factory:
    sprite = None
    sprite_size = None
    
    def __init__(self, x: float, y: float, health: int, tile_size: int, type: int = 0):

        self.x = x
        self.y = y
        self.max_health = health
        self.health = health
        self.production = 1
        self.last_production_time_ms = 0.0
        self.production_interval_ms = 2000.0
        self.sprite = None
        self.type = type
        
        # Load and scale sprite
        if self.sprite is None:
            try:
                BASE_PATH = os.path.dirname(__file__)
                ASSETS_PATH = os.path.join(BASE_PATH, "assets", "Sprites")
                
                sprite_path = os.path.join(ASSETS_PATH, "Factories", f"Factory-#{self.type + 1}.png")
                original = pygame.image.load(sprite_path)
                # Scale to fit tile size
                scale_factor = max(1, tile_size // original.get_width())
                new_size = original.get_width() * scale_factor
                self.sprite = pygame.transform.scale(original, (new_size, new_size))
                self.sprite_size = new_size
            except pygame.error as e:
                print(f"Could not load factory sprite: {e}")
                self.sprite = None
            
    def produce(self, current_time: float, wave_active: bool) -> int:
        if not wave_active:
            self.last_production_time_ms = current_time
            return 0
        if current_time - self.last_production_time_ms >= self.production_interval_ms:
            self.last_production_time_ms = current_time
            return self.production
        return 0
    
    def draw(self, surface: pygame.Surface):

        if self.sprite is not None:
            # Draw sprite
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            # Draw a rectangle if sprite failed to load
            pygame.draw.rect(surface, (100, 100, 100), 
                           (int(self.x - 15), int(self.y - 15), 30, 30))
        
        # Draw a healthbar
        offset_x = -4
        offset_y = 18
        healthbar_width = 30
        healthbar_height = 5
        health_ratio = self.health / self.max_health
        
        # Background rect - doesn't change width, represents missing health
        bg_rect = pygame.Rect(int(self.x - healthbar_width / 2 + offset_x), int(self.y + offset_y), healthbar_width, healthbar_height)
        pygame.draw.rect(surface, (255, 0, 0), bg_rect)
        
        # Foreground rect - scales width with remaining health
        fg_rect = pygame.Rect(int(self.x - healthbar_width / 2 + offset_x), int(self.y + offset_y), int(healthbar_width * health_ratio), healthbar_height)
        pygame.draw.rect(surface, (0, 255, 0), fg_rect)
