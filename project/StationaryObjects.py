# import pygame
import random

# import files
from Variabels import *
from ScreenObjects import *

class Wall(StationaryObject):
    def __init__(self,pos, wall_image):
        super().__init__(pos)
        self.image = wall_image
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def draw(self):
       return super().draw()

class Bush(StationaryObject):
    def __init__(self,pos, bush_image):
        super().__init__(pos)
        self.image = bush_image
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

# klasse met een methode om walls en bushes aan te maken op random posities onder bepaalde voorwaarden
available_positions = Screen.available_positions()
class GenerateObject: 
    def __init__(self, amount, object, image, player, bot1,bot2):
        self.amount = amount
        self.object = object
        self.image = image
        self.player = player
        self.bot1 = bot1
        self.bot2 = bot2
                    
    def generate(self):
        for i in range(self.amount):
            attempts = 0
            while True:
                x, y = random.choice(available_positions)
                object_pos = pygame.math.Vector2(x, y)

                # niet te dicht bij speler of bot
                if object_pos.distance_to(self.player.pos) <= 2 * player_size[0] or object_pos.distance_to(self.bot1) <= 4 * bot_size[0] or object_pos.distance_to(self.bot2) <= 4 * bot_size[0]:
                    continue # lus begint opnieuw

                # niet te dicht bij andere objecten
                too_close = False
                for obj in list_of_objects:
                    if object_pos.distance_to(pygame.math.Vector2(obj.rect.topleft)) < 3 * wall_size[0]:
                        too_close = True
                        break
                    
                if too_close:
                    attempts += 1
                    if attempts > 100:
                        break 
                    continue

                # alle checks zijn oké: object wordt geplaatst
                wall = self.object((x, y), self.image)
                list_of_objects.append(wall)
                available_positions.remove((x, y))
                break
