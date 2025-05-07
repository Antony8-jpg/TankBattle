import pygame
import math
import random
from queue import PriorityQueue

#import files
from Variabels import *
from ScreenObjects import *
from Powerups import *
from MovingObjects import *
from Player import *
from Grid import *

#TO DO:
#meerdere bots

pygame.init()
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()        
last_print_time = 0

class Bot(MovingObject):
    def __init__(self, pos,image,speed,angle):
        super().__init__(pos)
        self.image = image
        self.rect = self.image.get_rect(center = self.pos)
        self.speed = speed
        self.angle = angle
        self.last_shot_time = 0
        self.health = 5
        self.has_shield = False
        # movement state
        self.state = "follow"
        self.direction = pygame.math.Vector2(0, 1)
        self.path = []
        self.goal = None
        # timers
        self.last_shot_time = 0
        self.last_path_update_time = 0
        self.last_successful_path_time = pygame.time.get_ticks()
        self.state_starttime = pygame.time.get_ticks()
        self.state_duration = random.randint(2000, 4000)
        # random goal
        self.random_goal_x = random.randint(0, screen_length)
        self.random_goal_y = random.randint(0, screen_height)

    def bot_movement(self):
        current_time = pygame.time.get_ticks()
        self.start = Grid.screen_to_grid(self.pos) #startpositie van de bot in de grit

        #als er een shield is gaat de bot ervoor (1 kans op 3)
        #shield_targeted = False
        if shield_spawner.powerup and self.state != "shield": #shield state toevoegen om niet 2 shields te hebben
            if random.randint(1, 3) == 1:
                self.goal = Grid.screen_to_grid(pygame.math.Vector2(shield_spawner.powerup.rect.center))
                self.state = "shield" 
                self.state_starttime = current_time 
                self.state_duration = random.randint(3000, 5000) #gaat naar de shield enkel voor 4 seconden (om te voorkomen dat hij geblokkeerd is als hij zijn pad niet vindt)
                print("going for shield")
                #shield_targeted = True

        # state update
        if self.state != "shield" and current_time - self.state_starttime > self.state_duration:
            self.state_starttime = current_time
            self.state_duration = random.randint(2000, 4000)

            if self.pos.distance_to(player.pos) < 250: #volgt de player als die dichtbij is
                self.state = "follow"
            else:
                self.state = random.choices(["random", "follow"], weights=[3, 1])[0] # 75% kans om random , [0] om de string terug te geven ipv de lijst
                if self.state == "random": # bij random movement een random goal maken
                    self.random_goal_x = random.randint(0, screen_length)
                    self.random_goal_y = random.randint(0, screen_height)
            print(self.state) # om te zien wat er gebeurt

        # goals aanmaken/veranderen
        if self.state == "follow":
            self.goal = Grid.screen_to_grid(player.pos)
        elif self.state == "random":
            self.random_goal_vector = pygame.math.Vector2(self.random_goal_x, self.random_goal_y)
            self.goal = Grid.screen_to_grid(self.random_goal_vector)

        # pad updaten
        if current_time - self.last_path_update_time > 500: # elke 0.5 seconden om niet te laggen
            self.grid = Grid.build_grid() #grid nodig voor astar
            new_path = Grid.astar(self.start, self.goal, self.grid) #astar toepassen
            self.last_path_update_time = current_time

            if new_path:
                self.path = new_path
                self.last_successful_path_time = current_time
            elif current_time - self.last_successful_path_time > 1000:
                # als op moment van aanmaak van nieuw pad er geen pad kan worden aangemaakt op de eindpositie van de player dan zoekt de bot een open grid dichtbij -> alternative goal
                alternative_goal = self.find_closest_accessible_to_player()
                if alternative_goal and alternative_goal != self.goal:
                    alternative_path = Grid.astar(self.start, alternative_goal, self.grid)
                    if alternative_path: # als astar werkt
                        self.path = alternative_path
                        self.goal = alternative_goal
                        self.state = "follow"
                        self.last_successful_path_time = current_time
                        print("alternative path")

        #pad volgen
        if self.path:
            next_step = Grid.grid_to_screen(self.path[0])
            if self.pos.distance_to(next_step) < 5:
                self.path.pop(0)  #haal het eerste element eruit
                if len(self.path) == 0:
                    self.direction = pygame.math.Vector2(0, 0)

                    #als hij bij het einde geraakt van random/shield gaat hij over naar follow
                    if self.state in ["random", "shield"]:
                        self.state = "follow"
                        self.state_starttime = current_time
                        self.goal = Grid.screen_to_grid(player.pos)
                        self.path = Grid.astar(self.start, self.goal, self.grid)
                        if self.path:
                            self.last_successful_path_time = current_time
                    return
                next_step = Grid.grid_to_screen(self.path[0])

            self.direction = (next_step - self.pos).normalize()
            self.angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90

            # teken het pad voor visualisatie/debugging
            for grid in self.path:
                x = grid[0] * grid_size
                y = grid[1] * grid_size
                pygame.draw.rect(screen, (255, 255, 255), (x, y, grid_size, grid_size), 2)
        else:
            self.direction = pygame.math.Vector2(0, 0)

        # beweeg de bot position
        self.pos += self.speed * self.direction

    def find_closest_accessible_to_player(self): #alternatieve weg zoeken als de player dichtbij een obstacle is
        target_grid = Grid.screen_to_grid(player.pos)
        grid = self.grid

        search_radius = 1
        max_radius = max(grid_length, grid_height)

        while search_radius < max_radius:
            for dx in range(-search_radius, search_radius + 1):
                for dy in range(-search_radius, search_radius + 1):
                    x = target_grid[0] + dx
                    y = target_grid[1] + dy
                    # zoekt een vrije plek rond de player om naar toe te gaan
                    if 0 <= x < grid_length and 0 <= y < grid_height: 
                        if Grid.clear_area(grid, x, y, clearance=1):
                            return (x, y)
            search_radius += 1 # niet gevond -> straal groter maken
        return None  

    def bot_update(self,lengte,hoogte): # image van de bot updaten
        self.pos.x = max(0, min(self.pos.x, lengte))
        self.pos.y = max(0, min(self.pos.y, hoogte))

        rotated_bot_image = pygame.transform.rotate(self.image,self.angle)
        self.rect = rotated_bot_image.get_rect(center = self.pos)
        return rotated_bot_image, self.rect
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > bot_shooting_speed and self.direction.length_squared() != 0: # zodat hij niet schiet als die stil staat-> kan voor bug zorgen
            self.last_shot_time = current_time
            self.angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90
            bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
            bullet_list_bot.append(bullet)

    def reset(self):
        self.health = 5
        self.direction = pygame.math.Vector2(0, -1)
        self.pos = pygame.math.Vector2(screen_length - 100, screen_height / 2)
        self.has_shield = False

#klasse met een methode om walls en bushes aan te maken op random posities 
class GenerateObject: 
    def __init__(self, amount, object, image):
        self.amount = amount
        self.object = object
        self.image = image
                    
    def generate(self):
        for i in range(self.amount):
            attempts = 0
            while True:
                x, y = random.choice(available_positions)
                object_pos = pygame.math.Vector2(x, y)

                #niet te dicht bij speler of bot
                if object_pos.distance_to(player.pos) <= 2 * player_size[0] or object_pos.distance_to(bot.pos) <= 4 * bot_size[0]:
                    continue #lus begint opnieuw

                #niet te dicht bij andere objecten
                too_close = False
                for obj in list_of_objects:
                    if object_pos.distance_to(pygame.math.Vector2(obj.rect.topleft)) < 3 * wall_size[0]:
                        too_close = True
                        break
                    
                if too_close:
                    attempts += 1
                    if attempts > 100:
                        break 
                    continue #lus begint opnieuw

                #alles checks zijn oké: object wordt geplaatst
                wall = self.object((x, y), self.image)
                list_of_objects.append(wall)
                available_positions.remove((x, y))
                break

#objects
player = Player(player_pos, direction, player_speed, rotation_speed, angle,player_image)
bot = Bot(bot_pos,bot_image,bot_speed,bot_angle)

#walls and bushes generaten
"""list_of_objects = [] #walls en bushes worden in deze lijst geplaatst"""
available_positions = Screen.available_positions()
walls = GenerateObject(amount= wall_amount , object= Wall, image = wall_image)
walls.generate()
bushes = GenerateObject(amount= bush_amount , object= Bush, image= bush_image)
bushes.generate()

# #powerups aanmaken
shield_spawner = PowerUpSpawner(Shield, shield_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.has_shield and not bot.has_shield)
special_bullet_spawner = PowerUpSpawner(SpecialBulletPickup, special_bullet_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.has_special_bullet)
speedboost_spawner = PowerUpSpawner(SpeedBoost, speed_boost_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.speed_boost_active)


#gameloop
running = True
while running:
    clock.tick(20)
    """if game_state == "running":    
        screen.blit(game_background,(0,0))
    else:
        screen.blit(main_background, (0,0))"""
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    if game_state == "start":
        Screen.draw_start_screen()
        if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN] or start_button.clicked(event):  
            game_state = "running"
        if keys[pygame.K_i] or instructions_button.clicked(event):
            game_state = "instructions"
            
    elif game_state == "instructions":
        Screen.draw_instruction_screen()
        if keys[pygame.K_BACKSPACE] or back_to_homescreen_button.clicked(event):
            game_state = "start"
        if keys[pygame.K_KP_ENTER]:  
            game_state = "running"
    
    
    elif game_state == "running":
        screen.blit(game_background,(0,0))
        # alle functies laten runnen
        #player
        previous_pos = player.pos.copy()
        player.player_movement()  
        rotated_image, player_rect = player.update(screen_length, screen_height)
        player.shoot()
        player.shoot_special()
        player.reload_ammo()
        player_grid_pos = player.player_grid_pos() # dient voor niks denk ik
        
        #bot
        previous_bot_pos = bot.pos.copy()
        rotated_bot_image,bot_rect = bot.bot_update(screen_length,screen_height)
        bot.shoot()
        bot.bot_movement()
        
       #powerups: shield and special bullet
        shield_spawner.update()
        special_bullet_spawner.update()
        shield_spawner.draw()
        special_bullet_spawner.draw()
        speedboost_spawner.update()
        speedboost_spawner.draw()
               
        #managen bullets and collsion bullets of player and bot
        player.manage(bullet_list= bullet_list_player, yourobject = "player", other_object = bot)
        bot.manage(bullet_list = bullet_list_bot, yourobject = "bot", other_object = player)
        
        #collision player and wall, bot and wall
        for object in list_of_objects:
            if player.collision(object):
                player.pos = previous_pos
                player_rect.center = player.pos
            
            if bot.collision(object): #geen elif want anders gaat die alleen player doen bij twee botsingen die tegelijk zijn
                bot.pos = previous_bot_pos
                bot_rect.center = bot.pos
            
        #walls en bushes tekenen 
        for object in list_of_objects:
            if hasattr(object, "draw"):
                object.draw()
            
        # levens en ammo tekenen
        Screen.player_hearts(heart_pos,player.health,playerheart_image)
        Screen.bot_hearts(previous_bot_pos,bot.health,botheart_image)
        Screen.print_ammo(ammo_pos,bullet_image,player.ammo)
        Screen.draw_special_bullet_ammo(player)
        Screen.draw_reload_timer(player)
        Screen.draw_shield_indicator(player, bot)
        Screen.draw_speed_boost(player)
        player_rect = MovingObject.blit_rotated_image(screen, player.image, player.pos, player.angle, player_size)
        bot_rect = MovingObject.blit_rotated_image(screen, bot.image, bot.pos, bot.angle, bot_size)

        #rect tekenen om collision te begrijpen
        #pygame.draw.rect(screen, (255, 0, 0), player_rect, 2)
        #pygame.draw.rect(screen, (0, 0, 255), bot_rect, 2)        

        if player.health <= 0:
            game_state = "lost"
        elif bot.health <= 0:
            game_state = "won"

    # Win or Loss       
    elif game_state in ["won", "lost","start"]:
        #reset alles
        bullet_list_player.clear()
        bullet_list_bot.clear()
        shield_spawner.reset()
        special_bullet_spawner.reset()
        active_powerups.clear()
        player.reset()
        bot.reset()
        
        #walls and bushes generaten
        list_of_objects.clear()
        available_positions = Screen.available_positions()
        walls = GenerateObject(amount= wall_amount , object= Wall, image = wall_image)
        walls.generate()
        bushes = GenerateObject(amount= bush_amount , object= Bush, image= bush_image)
        bushes.generate()
        
        if game_state == "won":
            screen.blit(winning_background,(0,0))
            Screen.draw_end_screen("YOU WON!")
            won_button.draw(screen)
        
        else:
            screen.blit(lost_background,(0,0))
            Screen.draw_end_screen("YOU LOST!")
            lost_button.draw(screen)
        
        if keys[pygame.K_r] or keys[pygame.K_KP_ENTER] or won_button.clicked(event) or lost_button.clicked(event):  
            game_state = "running"
            
        if keys[pygame.K_i]:
            game_state = "instructions"


    # exiting
    if keys[pygame.K_ESCAPE]:
        running = False
    
    pygame.display.update()

pygame.quit()
