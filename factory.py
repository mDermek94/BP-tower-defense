
import pygame
from enemy import Enemy
from typing import List
from math import *

class Factory:
    sprite = None
    sprite_size = None
    
    def __init__(self, x: float, y: float, health: int, tile_size: int):

        self.x = x
        self.y = y
        self.health = health
        self.production = 1
        self.price = 5
        self.last_production_time_ms = 0.0
        self.production_interval_ms = 2000.0
        
        # Load and scale sprite
        if Factory.sprite is None:
            try:
                original = pygame.image.load("Sprites/Factories/Factory-#1.png")
                # Scale to fit tile size
                scale_factor = max(1, tile_size // original.get_width())
                new_size = original.get_width() * scale_factor
                Factory.sprite = pygame.transform.scale(original, (new_size, new_size))
                Factory.sprite_size = new_size
            except pygame.error as e:
                print(f"Could not load factory sprite: {e}")
                Factory.sprite = None
            
    def produce(self, current_time: float, wave_active: bool) -> int:
        if not wave_active:
            self.last_production_time_ms = current_time
            return 0
        if current_time - self.last_production_time_ms >= self.production_interval_ms:
            self.last_production_time_ms = current_time
            return self.production
        return 0
    
    def draw(self, surface: pygame.Surface):

        if Factory.sprite is not None:
            # Draw sprite
            rect = Factory.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(Factory.sprite, rect)
        else:
            # Draw a rectangle if sprite failed to load
            pygame.draw.rect(surface, (100, 100, 100), 
                           (int(self.x - 15), int(self.y - 15), 30, 30))