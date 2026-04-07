
import pygame
from enemy import Enemy
from typing import List
from math import *

class Bullet:
    def __init__(self, x: float, y: float, enemy: Enemy, velocity: float = 2.0, type: int = 0):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.facing = (1.0, 1.0)
        self.target_x = 0
        self.target_y = 0
        self.reached_target = False
        self.target = enemy
        self.type = type
        
    def get_target(self, enemy: Enemy):
        a = pow(enemy.velocity, 2) - pow(self.velocity, 2)
        b = 2 * ((enemy.x - self.x) * enemy.velocity * enemy.facing[0] + (enemy.y - self.y) * enemy.velocity * enemy.facing[1])
        c = pow((enemy.x - self.x), 2) + pow((enemy.y - self.y), 2)

        disc = pow(b, 2) - 4 * a * c

        # If quadratic is invalid (a = 0 or discriminant <= 0), aim directly without leading
        if a == 0 or disc <= 0:
            self.target_x = enemy.x
            self.target_y = enemy.y
            diff_x = self.target_x - self.x
            diff_y = self.target_y - self.y
            distance = sqrt(diff_x * diff_x + diff_y * diff_y) or 1.0
            self.facing = (diff_x / distance, diff_y / distance)
            self.reached_target = False
            return

        root_disc = sqrt(disc)
        x1 = (-b + root_disc) / (2 * a)
        x2 = (-b - root_disc) / (2 * a)

        if (x1 < 0 and x2 < 0):
            # If bullet is too slow, aim directly without leading
            self.target_x = enemy.x
            self.target_y = enemy.y
            diff_x = self.target_x - self.x
            diff_y = self.target_y - self.y
            distance = sqrt(diff_x * diff_x + diff_y * diff_y) or 1.0
            self.facing = (diff_x / distance, diff_y / distance)
            self.reached_target = False
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
        distance = sqrt(pow(diff_x, 2) + pow(diff_y, 2)) or 1.0
        
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
        if self.type == 0:
            color = (98, 96, 255)
        elif self.type == 1:
            color = (255, 96, 96)
        elif self.type == 2:
            color = (255, 253, 123)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)
        

class Tower:
    sprite = None
    sprite_size = None
    
    def __init__(self, x: float, y: float, health: int, tile_size: int, type: int = 0):

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
                original = pygame.image.load(f"Sprites/Towers/Tower-#{self.type + 1}.png")
                print(f"Used Tower Sprite {self.type + 1}")
                # Scale to fit tile size
                scale_factor = max(1, tile_size // original.get_width())
                new_size = original.get_width() * scale_factor
                self.sprite = pygame.transform.scale(original, (new_size, new_size))
                self.sprite_size = new_size
            except pygame.error as e:
                print(f"Could not load tower sprite: {e}")
                self.sprite = None
    
    def enemy_distance(self, enemy_x: float, enemy_y: float):
        dx = enemy_x - self.x
        dy = enemy_y - self.y
        return dx*dx + dy*dy
    
    def get_target(self, enemies: List[Enemy]):
        
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
            
    
    def shoot(self, current_time: int, enemies: List[Enemy], bullets: List[Bullet]):
        
        if current_time - self.last_shot_time < self.shot_cooldown:
            return
        
        target = self.get_target(enemies)
        
        if target is None:
            return
        
        bullet = Bullet(self.x, self.y, target, velocity=self.bullet_speed, type=self.type)
        
        bullet.get_target(target)
        
        # if bullet.reached_target:
        #     bullet.target_x = target.x
        #     bullet.target_y = target.y
        #     dx = target.x - self.x
        #     dy = target.y - self.y
        #     dist = sqrt(dx*dx + dy*dy) or 1.0
        #     bullet.facing = (dx/dist, dy/dist)
        #     bullet.reached_target = False
            
        bullets.append(bullet)
        self.last_shot_time = current_time
    
    def update(self, current_time: int, enemies: List[Enemy], bullets: List[Bullet]):
        self.shoot(current_time, enemies, bullets)
    
    def draw(self, surface: pygame.Surface):

        if self.sprite is not None:
            # Draw sprite
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            # Draw a rectangle if sprite failed to load
            pygame.draw.rect(surface, (100, 100, 100), 
                           (int(self.x - 15), int(self.y - 15), 30, 30))
