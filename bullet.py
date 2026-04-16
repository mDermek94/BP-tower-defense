import pygame
from math import *

class Bullet:
    def __init__(self, x: float, y: float, velocity: float = 2.0, type: int = 0, is_enemy_bullet: bool = False):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.facing = (1.0, 1.0)
        self.target_x = 0
        self.target_y = 0
        self.type = type
        self.is_enemy_bullet = is_enemy_bullet
        self.factory_damage = 10
        
    def get_target(self, enemy):
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
        
    def get_target_factory(self, factory):
        # Used with enemies capable of shooting at factories, simply targets a standing object and therefore doesn't need any bullet leading
        
        self.target_x = factory.x
        self.target_y = factory.y
        diff_x = self.target_x - self.x
        diff_y = self.target_y - self.y
        distance = sqrt(diff_x * diff_x + diff_y * diff_y) or 1.0
        self.facing = (diff_x / distance, diff_y / distance)
        
    def move(self, delta_time):
        self.x += self.facing[0] * self.velocity * delta_time
        self.y += self.facing[1] * self.velocity * delta_time
            
    def draw(self, surface: pygame.Surface, size: float = 2.0):
        if self.type == 0:
            color = (98, 96, 255)
        elif self.type == 1:
            color = (255, 96, 96)
        elif self.type == 2 and not self.is_enemy_bullet:
            color = (255, 253, 123)
        elif self.type == 2 and self.is_enemy_bullet:
            color = (80, 80, 120)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)
        