
import pygame
from bullet import Bullet
from math import *
import os

class Tower:
    sprite = None
    sprite_size = None
    
    def __init__(self, x, y, health, tile_size, type = 0):

        self.x = x
        self.y = y
        self.health = health
        self.shoot_radius = 2.5 * tile_size
        self.shot_cooldown = 800
        self.last_shot_time = 0
        self.bullet_speed = 3.2
        self.type = type
        self.sprite = None
        self.sprite_size = 1
        
        if self.type == 1:
            self.shot_cooldown = 600
        elif self.type == 2:
            self.shot_cooldown = 500
        
        # Load and scale sprite
        if self.sprite is None:
            try:
                BASE_PATH = os.path.dirname(__file__)
                ASSETS_PATH = os.path.join(BASE_PATH, "assets", "Sprites")
                
                sprite_path = os.path.join(ASSETS_PATH, "Towers", f"Tower-#{self.type + 1}.png")
                original = pygame.image.load(sprite_path)
                
                # Scale to fit tile size
                scale_factor = max(1, tile_size // original.get_width())
                new_size = original.get_width() * scale_factor
                self.sprite = pygame.transform.scale(original, (new_size, new_size))
                self.sprite_size = new_size
            except pygame.error as e:
                print(f"Could not load tower sprite: {e}")
                self.sprite = None
    
    def enemy_distance(self, enemy_x, enemy_y):
        dx = enemy_x - self.x
        dy = enemy_y - self.y
        return dx*dx + dy*dy
    
    def get_target(self, enemies):
        
        best_enemy = None
        best_distance = self.shoot_radius * self.shoot_radius
    
        for e in enemies:
            if e.reached_end:
                continue
            distance = self.enemy_distance(e.x, e.y)
            if distance <= best_distance:
                best_distance = distance
                best_enemy = e
        return best_enemy
            
    
    def shoot(self, current_time, enemies, bullets):
        
        if current_time - self.last_shot_time < self.shot_cooldown:
            return
        
        target = self.get_target(enemies)
        
        if target is None:
            return
        
        bullet = Bullet(self.x, self.y, velocity=self.bullet_speed, type=self.type)
        
        bullet.get_target(target)
            
        bullets.append(bullet)
        self.last_shot_time = current_time
    
    def draw(self, surface):

        if self.sprite is not None:
            # Draw sprite
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            # Draw a rectangle if sprite failed to load
            pygame.draw.rect(surface, (100, 100, 100), 
                           (int(self.x - 15), int(self.y - 15), 30, 30))

    def update(self, current_time, enemies, bullets, surface):
        self.shoot(current_time, enemies, bullets)
        self.draw(surface)
