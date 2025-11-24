
import pygame
from enemy import Enemy
from typing import List
from math import *

class Bullet:
    def __init__(self, x: float, y: float, velocity: float = 2.0):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.facing = (1.0, 1.0)
        self.target_x = 0
        self.target_y = 0
        self.reached_target = False
        
    def get_target(self, enemy: Enemy):
        a = pow(enemy.velocity, 2) - pow(self.velocity, 2)
        b = 2 * ((enemy.x - self.x) * enemy.velocity * enemy.facing[0] + (enemy.y - self.y) * enemy.velocity * enemy.facing[1])
        c = pow((enemy.x - self.x), 2) + pow((enemy.y - self.y), 2)
        
        x1 = (-b + sqrt(pow(b, 2) - 4 * a * c)) / (2 * a)
        x2 = (-b - sqrt(pow(b, 2) - 4 * a * c)) / (2 * a)
        
        if (x1 < 0 and x2 < 0):
            print("Bullet is too slow to hit the enemy.")
            self.reached_target = True
            return
        else:
            if x1 < 0 and x2 >= 0:
                result = x2
            elif x2 < 0 and x1 >= 0:
                result = x1
            else:
                result = min(x1, x2)
                
        self.target_x = enemy.x + result * enemy.velocity * enemy.facing[0]
        self.target_y = enemy.y + result * enemy.velocity * enemy.facing[1]
        
        diff_x = self.target_x - self.x
        diff_y = self.target_y - self.y
        distance = sqrt(pow(diff_x, 2) + pow(diff_y, 2))
        
        facing_x = diff_x / distance
        facing_y = diff_y / distance
        
        self.facing = (facing_x, facing_y)
        
    def move(self, delta_time):
        self.x += self.facing[0] * self.velocity * delta_time
        self.y += self.facing[1] * self.velocity * delta_time
        
        dist_to_target = sqrt(pow(self.target_x - self.x, 2) + pow(self.target_y - self.y, 2))
        if dist_to_target < self.velocity * delta_time:
            self.reached_target = True
    
    def draw(self, surface: pygame.Surface, size: float = 2.0):
        pygame.draw.circle(surface, (20, 20, 20), (int(self.x), int(self.y)), size)
        

class Tower:
    sprite = None
    sprite_size = None
    
    def __init__(self, x: float, y: float, health: int, tile_size: int):

        self.x = x
        self.y = y
        self.health = health
        self.shoot_radius = 2.5 * tile_size
        
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
