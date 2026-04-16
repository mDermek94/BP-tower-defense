
import pygame
import math
from typing import List
from factory import Factory
from bullet import Bullet


class Enemy:
    def __init__(self, x: float, y: float, type: int = 0, shot_cooldown: int = 3000):

        self.x = x
        self.y = y
        self.size = 8
        self.facing = (1.0, 0.0)
        self.velocity = 2.5
        self.color = (255, 100, 100)
        self.health = 100
        self.type = type
        self.last_shot_time = 0
        self.shot_cooldown = shot_cooldown
        self.bullet_speed = 3
            
        if self.type == 1:
            self.health = 100
            self.velocity = 3.0
            self.color = (100, 255, 100)
        elif self.type == 2:
            self.health = 100
            self.velocity = 3.5
            self.color = (100, 100, 255)
        
        self.reward = 1 + 1 * self.type
        self.damage = 10
        
        self.path = []
        self.current_waypoint_index = 0
        self.reached_end = False
        
    def set_path(self, waypoints: list):
        self.path = waypoints
        self.current_waypoint_index = 0
        self.reached_end = False
        
        if self.path:
            self.x = self.path[0]["x"]
            self.y = self.path[0]["y"]
            if self.path[0]["dir"] is not None:
                self.facing = self._dir_to_vector(self.path[0]["dir"])
        
    def follow_path(self, delta_time: float = 1.0):
        if self.reached_end or not self.path:
            return
        
        distance_to_move = self.velocity * delta_time
        
        while distance_to_move > 0 and not self.reached_end:
            if self.current_waypoint_index >= len(self.path):
                self.reached_end = True
                break
            
            target_wp = self.path[self.current_waypoint_index]
            target_x = target_wp["x"]
            target_y = target_wp["y"]
            
            # Calculate distance to current waypoint
            dx = target_x - self.x
            dy = target_y - self.y
            dist_to_target = math.sqrt(dx * dx + dy * dy)
            
            if dist_to_target <= distance_to_move:
                self.x = target_x
                self.y = target_y
                distance_to_move -= dist_to_target
                
                # Next waypoint
                self.current_waypoint_index += 1
                
                # Update facing direction
                if self.current_waypoint_index < len(self.path):
                    next_dir = self.path[self.current_waypoint_index - 1]["dir"]
                    if next_dir is not None:
                        self.facing = self._dir_to_vector(next_dir)
                else:
                    # Reached the end
                    self.reached_end = True
            else:
                if dist_to_target > 0:
                    move_ratio = distance_to_move / dist_to_target
                    self.x += dx * move_ratio
                    self.y += dy * move_ratio
                distance_to_move = 0
    
    def _dir_to_vector(self, direction: str) -> tuple:

        if direction == "right":
            return (1.0, 0.0)
        elif direction == "left":
            return (-1.0, 0.0)
        elif direction == "down":
            return (0.0, 1.0)
        elif direction == "up":
            return (0.0, -1.0)
        else:
            return (1.0, 0.0)
    
    def get_target(self, factories: List[Factory]):
        
        min_dist = 100000000
        
        best_factory = None # Shoot at closest
        
        for f in factories:
            dx = f.x - self.x
            dy = f.y - self.y
            dist = dx*dx + dy*dy
            if dist < min_dist:
                min_dist = dist
                best_factory = f
                
        return best_factory
            
    
    def shoot(self, current_time: int, factories: List[Factory], bullets: List[Bullet]):
        
        if current_time - self.last_shot_time < self.shot_cooldown:
            return
        
        target = self.get_target(factories)
        
        if target is None:
            return
        
        bullet = Bullet(self.x, self.y, velocity=self.bullet_speed, type=self.type, is_enemy_bullet=True)
        
        bullet.get_target_factory(target)
        
        bullets.append(bullet)
        self.last_shot_time = current_time
    
    def draw(self, surface: pygame.Surface, size: int = 8):

        self.size = size

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        end_x = int(self.x + self.facing[0] * self.size * 1.5)
        end_y = int(self.y + self.facing[1] * self.size * 1.5)
        pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (end_x, end_y), 2)
        
    def update(self, current_time: int, factories, bullets: List[Bullet], surface: pygame.Surface, size: int = 8):
        if self.type == 2:
            self.shoot(current_time, factories, bullets)
        self.draw(surface, size)
