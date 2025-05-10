import pygame
import random

# import files
from Variabels import *

class PowerUp(StationaryObject):
    def __init__(self, pos, image):
        super().__init__(pos)
        self.image = image
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def apply_effect(self, target):
        pass

    def draw(self):
        super().draw()

class Shield(PowerUp):
    def apply_effect(self, target):
        target.has_shield = True

class SpecialBulletPickup(PowerUp):
    def apply_effect(self, target):
        target.has_special_bullet = True

class SpeedBoost(PowerUp):
    def __init__(self, pos, image):
        super().__init__(pos, image)

    def apply_effect(self, player):
        player.speed_boost_active = True
        player.speed_boost_start_time = pygame.time.get_ticks()
   
class PowerUpSpawner:
    def __init__(self, powerup_class, image, player, bot1,bot2, list_of_objects, available_positions, condition_func):
        self.powerup_class = powerup_class
        self.image = image
        self.player = player
        self.bot = bot1
        self.bot2 = bot2
        self.list_of_objects = list_of_objects
        self.available_positions = available_positions
        self.condition_func = condition_func  # dit is een functie die nodig is om voorwaarden te checken, maar die verschillend is voor elke powerup bv. not player.has_shield
        self.powerup = None
        self.next_spawn_time = 0
        self.timer_active = False


    def update(self):
        current_time = pygame.time.get_ticks()

        # tijdsinterval voor het spawnen van de powerup starten
        if not self.timer_active and self.powerup is None and self.condition_func(self.player): 
            self.next_spawn_time = current_time + random.randint(5000, 20000) # poewerups worden random gespawned tussen 5 en 20 seconden 
            self.timer_active = True

        # positie voor de powerrup zoeken
        if current_time >= self.next_spawn_time and self.powerup is None and self.condition_func(self.player):
            random.shuffle(self.available_positions) # lijst random shuffelen
            for (x, y) in self.available_positions:
                new_pos = pygame.math.Vector2(x, y)
                
                powerup_safe_to_spawn = True
                for obj in self.list_of_objects + active_powerups: # extra controleren of powerup op een veilige locatie wordt gespawnd
                    if obj.rect.collidepoint(x, y):
                        powerup_safe_to_spawn = False
                        break
                
                if new_pos.distance_to(self.player.pos) > 200 and new_pos.distance_to(self.bot.pos) > 200 and powerup_safe_to_spawn:
                    self.powerup = self.powerup_class((x, y), self.image)
                    active_powerups.append(self.powerup)
                    self.timer_active = False
                    break
        
        # collision met player
        if self.powerup and self.player.rect.colliderect(self.powerup.rect):
            self.powerup.apply_effect(self.player)
            if self.powerup in active_powerups: #voorkomt dat een powerup wordt verwijdert terwijl het niet in de lijst zit
                active_powerups.remove(self.powerup)
            self.powerup = None
            
        # collision met bot1 (enkel voor shield)
        if self.powerup and isinstance(self.powerup, Shield) and self.bot.rect.colliderect(self.powerup.rect):
            self.powerup.apply_effect(self.bot)
            if self.powerup in active_powerups:
                active_powerups.remove(self.powerup)
                self.powerup = None
            self.powerup = None
        
        # collision met bot2 (enkel voor shield)
        if self.powerup and isinstance(self.powerup, Shield) and self.bot2.rect.colliderect(self.powerup.rect):
            self.powerup.apply_effect(self.bot2)
            if self.powerup in active_powerups:
                active_powerups.remove(self.powerup)
                self.powerup = None
            self.powerup = None

    def draw(self):
        if self.powerup:
            self.powerup.draw()

    def reset(self):
        self.powerup = None
        self.timer_active = False
        self.next_spawn_time = 0
