import pygame
import math

# import files
from Variabels import *
from ScreenObjects import *
from MovingObjects import *

class Player(MovingObject):
    def __init__(self,pos,direction,player_speed,rotation_speed,angle,playerImg):
        super().__init__(pos)
        self.direction = direction
        self.rotation_speed = rotation_speed
        self.angle = angle
        self.image = playerImg
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size[0], player_size[1])
        self.last_shot_time = 0 # timer voor bullets    
        self.ammo = 3
        self.last_reload_time = pygame.time.get_ticks()
        self.health = player_health
        self.has_special_bullet = False
        self.has_shield = False
        self.speed_boost_active = False
        self.speed_boost_start_time = 0
        self.base_speed = player_speed

    def player_movement(self):
        # speed updaten en powerup checken
        if self.speed_boost_active and pygame.time.get_ticks() - self.speed_boost_start_time > speed_boost_duration:
            self.speed_boost_active = False
        
        actual_speed = self.base_speed * (1.5 if self.speed_boost_active else 1) # speed wordt vermenigvuldigd met 1.5 als de speed boost actief is
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.speed = actual_speed
        elif keys[pygame.K_DOWN]:
            self.speed = -actual_speed
        else:
            self.speed = 0  
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed 
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed
    
    def update(self,lengte,hoogte):
        dy = math.cos(math.radians(self.angle))
        dx = math.sin(math.radians(self.angle))
        self.direction = -pygame.math.Vector2(dx, dy)
        # beweging samenvoegen
        self.pos += self.speed * self.direction
        
        rotated_image = pygame.transform.rotate(self.image,self.angle)
        self.rect.center = self.pos
        self.rect = rotated_image.get_rect(center = self.pos)
        
        self.pos.x = max(0, min(self.pos.x, lengte))
        self.pos.y = max(0, min(self.pos.y, hoogte))
        
        return rotated_image, self.rect   
    
    def reload_ammo(self):
        current_time = pygame.time.get_ticks()        
        if self.ammo < max_ammo and current_time - self.last_reload_time >= bullet_cooldown:
            self.ammo += 1
            self.last_reload_time = current_time
    
    def shoot(self):
        current_time = pygame.time.get_ticks()  
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_SPACE] and self.ammo > 0 and current_time - self.last_shot_time > 333: 
            self.last_shot_time = current_time #tijd updaten
            bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
            bullet_list_player.append(bullet)
            self.ammo -= 1  
            
    def shoot_special(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and self.has_special_bullet and current_time - self.last_shot_time > 500:
            self.last_shot_time = current_time
            special_bullet = SpecialBullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, special_bullet_image)
            bullet_list_player.append(special_bullet)
            self.has_special_bullet = False
    
    def reset(self):
        self.health = player_health
        self.ammo = max_ammo
        self.has_special_bullet = False
        self.direction = pygame.math.Vector2(0, 1)
        self.pos = pygame.math.Vector2(100, screen_height / 2)
        self.angle = 0
        self.has_shield = False
        self.speed_boost_active = False
        self.speed_boost_start_time = 0
