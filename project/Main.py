import pygame
import math
import random

# import files
from Variabels import *
from ScreenObjects import *
from Powerups import *
from MovingObjects import *
from Player import *
from Grid import *
from StationaryObjects import *

pygame.init()
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()        

# bot klasse staat in deze file omdat alles wordt gebruikt in de bot klasse
class Bot(MovingObject):
    def __init__(self, pos,image,speed,angle,start_pos,bullet_list,is_alive):
        super().__init__(pos)
        self.image = image
        self.rect = self.image.get_rect(center = self.pos)
        self.speed = speed
        self.angle = angle
        self.start_pos = start_pos
        self.bullet_list = bullet_list
        self.alive = is_alive
        self.last_shot_time = 0
        self.health = bot_health
        self.has_shield = False
        # movement state
        self.state = "random"
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
        # cooldown toevoegen zodat de bots niet altijd naar de shield gaan (zonder cooldown-> 100% kans)
        self.last_shield_check_time = 0
        self.shield_check_cooldown = random.randint(3000, 7000)

    def bot_movement(self):
        current_time = pygame.time.get_ticks()
        self.start = Grid.screen_to_grid(self.pos) # startpositie van de bot in de grit

        # als er een shield is gaat de bot ervoor (1 kans op 2)
        if shield_spawner.powerup and self.state != "shield" and self.pos.distance_to(player.pos)>200: #shield state toevoegen om niet 2 shields te hebben
            if current_time - self.last_shield_check_time > self.shield_check_cooldown:
                self.last_shield_check_time = current_time
                self.shield_check_cooldown = random.randint(2000, 4000)  # reset cooldown
                if random.randint(1, 2) == 1:
                    self.goal = Grid.screen_to_grid(pygame.math.Vector2(shield_spawner.powerup.rect.center))
                    self.state = "shield" 
                    self.state_starttime = current_time 
                    self.state_duration = random.randint(3000, 5000) # gaat naar het shield enkel voor 4 seconden (om te voorkomen dat hij geblokkeerd is als hij zijn pad niet vindt)
                    
        # state update
        if self.state == "shield" and shield_spawner.powerup == None: # als het shield weg is en bot was in shield state gaat hij naar follow
            self.state = "follow"
            
        if self.state != "shield" and current_time - self.state_starttime > self.state_duration:
            self.state_starttime = current_time
            self.state_duration = random.randint(2000, 4000)

            if self.pos.distance_to(player.pos) < 250: # volgt de player als deze dichtbij is
                self.state = "follow"
            else:
                self.state = random.choices(["random", "follow"], weights=[3, 1])[0] # 75% kans op random , [0] om de string terug te geven ipv de lijst
                if self.state == "random": # bij random movement een random goal maken
                    self.random_goal_x = random.randint(0, screen_length)
                    self.random_goal_y = random.randint(0, screen_height)

        # goals aanmaken/veranderen
        if self.state == "follow":
            self.goal = Grid.screen_to_grid(player.pos)
        elif self.state == "random":
            self.random_goal_vector = pygame.math.Vector2(self.random_goal_x, self.random_goal_y)
            self.goal = Grid.screen_to_grid(self.random_goal_vector)

        # pad maken
        if current_time - self.last_path_update_time > 500: # elke 0.5 seconden om niet te laggen
            self.grid = Grid.build_grid() # grid nodig voor astar
            new_path = Grid.astar(self.start, self.goal, self.grid) # astar toepassen
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

        # pad volgen
        if self.path  and self.pos.distance_to(player.pos) > 60:
            self.speed  = bot_speed
            next_step = Grid.grid_to_screen(self.path[0])
            if self.pos.distance_to(next_step) < 5:
                self.path.pop(0)  # haal het eerste element eruit
                if len(self.path) == 0:
                    self.direction = pygame.math.Vector2(0, 0)
                    # als hij bij het einde geraakt van random/shield gaat hij over naar follow
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
            
        else:
            self.speed = 0
            self.direction = (player.pos-self.pos).normalize()

        # beweeg de bot position
        self.pos += self.speed * self.direction

    def find_closest_accessible_to_player(self): # alternatieve weg zoeken als de player dichtbij een obstacle is
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
            search_radius += 1 # niet gevonden -> straal groter maken
        return None  

    def bot_update(self,lengte,hoogte): # image van de bot updaten
        self.pos.x = max(0, min(self.pos.x, lengte))
        self.pos.y = max(0, min(self.pos.y, hoogte))

        self.rotated_image = pygame.transform.rotate(self.image,self.angle)
        self.rect = self.rotated_image.get_rect(center = self.pos)
        return self.rotated_image, self.rect
    
    def shoot(self,bullet_list):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > bot_shooting_speed: 
            self.last_shot_time = current_time
            self.angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90
            bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
            bullet_list.append(bullet)

    def reset(self):
        self.health = 5
        self.direction = pygame.math.Vector2(0, -1)
        self.has_shield = False
        self.pos = self.start_pos.copy()
        self.bullet_list = []

# objects aanmaken
player = Player(player_pos, direction, player_speed, rotation_speed, angle,player_image)
bot1 = Bot(bot_pos,bot_image,bot_speed,bot_angle,bot1_start_pos,[],True)
bot2 = Bot(bot2_pos,bot_image,bot_speed,bot_angle,bot2_start_pos,[],False)
bots= [bot1] # bot2 enkel appenden als bij medium difficulty

# walls and bushes generaten
walls = GenerateObject(wall_amount, Wall, wall_image, player, bot1_start_pos,bot2_start_pos)
walls.generate()
bushes = GenerateObject(bush_amount, Bush, bush_image, player, bot1_start_pos,bot2_start_pos)
bushes.generate()

# powerups aanmaken
shield_spawner = PowerUpSpawner(Shield, shield_image, player, bot1, bot2, list_of_objects, available_positions, condition_func = lambda x: not x.has_shield and not bot1.has_shield)
special_bullet_spawner = PowerUpSpawner(SpecialBulletPickup, special_bullet_image, player, bot1, bot2, list_of_objects, available_positions, condition_func = lambda x: not x.has_special_bullet)
speedboost_spawner = PowerUpSpawner(SpeedBoost, speed_boost_image, player, bot1, bot2, list_of_objects, available_positions, condition_func = lambda x: not x.speed_boost_active)

game_state = "start"  # verschillende states: "start", "instructions", "gamemode", "running", "won", "lost"
# game mode variabelen
previous_gamemode = "easy" 
medium_unlocked = False
hard_unlocked = False
medium_unlocked_counter = 0
hard_unlocked_counter = 0
medium_just_unlocked = False # twee variabelen die ervoor zorgen dat de counter maar 1 keer omhoog gaat, anders gaat elke frame de counter omhoog
hard_just_unlocked = False

# gameloop
running = True
while running:
    clock.tick(20)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # start window
    if game_state == "start":
        Screen.draw_start_screen()
        if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN] or start_button.clicked(event):  
            game_state = "gamemode"
        if keys[pygame.K_i] or instructions_button.clicked(event):
            game_state = "instructions"
    
    # instruction window       
    elif game_state == "instructions":
        Screen.draw_instruction_screen()
        if keys[pygame.K_BACKSPACE] or back_to_homescreen_button.clicked(event):
            game_state = "start"
        if keys[pygame.K_KP_ENTER]or start_button.clicked(event):  
            game_state = "gamemode"
    
    # gamemode window
    elif game_state == "gamemode":
        Screen.draw_gamemode_screen()
        if easy_button.clicked(event):
            bot2.alive = False
            bot_shooting_speed = 2000
            bot_speed = 3
            previous_gamemode = "easy"
            game_state = "running"
            player.has_special_bullet = False
            if len(bots) >1:
                bots.remove(bot2) 
            
        elif medium_button.clicked(event) and medium_unlocked:
            player.has_special_bullet = True
            bot2.alive = True # tweede bot wordt geactiveerd
            bot_shooting_speed = 1500 # schiet sneller
            bot_speed = 5 # gaat sneller
            previous_gamemode = "medium"
            game_state = "running"
            
        elif hard_button.clicked(event) and hard_unlocked:
            player.has_special_bullet = True
            bot2.alive = True
            bot_shooting_speed = 1000 # shiet nog sneller
            bot_speed = 7 # gaat nog sneller
            game_state = "running"
        
        if not medium_unlocked: # lock image blitten
            screen.blit(lock_image, (screen_length//2 +100,355))
            
        if not hard_unlocked:
            screen.blit(lock_image, ((screen_length//2 +100,455)))
        bots.clear()
        for bot in [bot1,bot2]:
            if bot.alive:
                bots.append(bot)
    # game window        
    elif game_state == "running":
        screen.blit(game_background,(0,0))
        
        # movingobjects laten runnen
        previous_pos = player.pos.copy()
        player.player_movement()  
        rotated_image, player_rect = player.update(screen_length, screen_height)
        player.shoot()
        player.shoot_special()
        player.reload_ammo()
        player.manage(bullet_list_player) 
        player.bullet_collisions(bullet_list_player, "player", bot1)
        player.bullet_collisions(bullet_list_player, "player", bot2)
        
        for bot in bots:
            if bot.alive:
                bot.previous_bot_pos = bot.pos.copy()
                bot.rotated_image,bot.rect = bot.bot_update(screen_length,screen_height)
                bot.shoot(bot.bullet_list)
                bot.bot_movement()
                bot.manage(bot.bullet_list) # bullets updaten
                bot.bullet_collisions(bullet_list = bot.bullet_list, yourobject = "bot", other_object = player)
                Screen.bot_hearts(bot.previous_bot_pos,bot.health,botheart_image)
                bot.rect = MovingObject.blit_rotated_image(screen, bot.image, bot.pos, bot.angle, bot_size)
        
        # powerups: shield, special bullet en speedboost updaten en tekenen
        shield_spawner.update()
        special_bullet_spawner.update()
        shield_spawner.draw()
        special_bullet_spawner.draw()
        speedboost_spawner.update()
        speedboost_spawner.draw()
               
        # collision player and wall, bot and wall
        for object in list_of_objects:
            if player.collision(object):
                player.pos = previous_pos
                player_rect.center = player.pos
            for bot in bots:
                if bot.collision(object): # geen elif want anders gaat die alleen de player uitvoeren bij twee botsingen die tegelijk zijn
                    bot.pos = bot.previous_bot_pos
                    bot.rect_center = bot.previous_bot_pos
        
        # walls en bushes tekenen 
        for object in list_of_objects:
            if hasattr(object, "draw"):
                object.draw()
            
        # levens en ammo tekenen
        Screen.player_hearts(heart_pos,player.health,playerheart_image)
        Screen.print_ammo(ammo_pos,bullet_image,player.ammo)
        Screen.draw_special_bullet_ammo(player)
        Screen.draw_reload_timer(player)
        Screen.draw_shield_indicator(player, bot1,bot2)
        Screen.draw_speed_boost(player)
        player_rect = MovingObject.blit_rotated_image(screen, player.image, player.pos, player.angle, player_size)

        for bot in bots:
            if bot.health <=0 and bot.alive:
                kill_sound.play()
                bot.alive = False
        if player.health <= 0:
            game_state = "lost"
        elif bot1.health <= 0 and (bot2.health <=0 or bot2.alive == False):
            game_state = "won"

    # Win or Lost state     
    elif game_state in ["won", "lost","start"]:
        # reset alles
        bot1.alive = True
        for bot in bots:
            bot.reset()            
        bullet_list_player.clear()
        shield_spawner.reset()
        special_bullet_spawner.reset()
        speedboost_spawner.reset()
        active_powerups.clear()
        player.reset()
        
        if game_state == "won":
            screen.blit(winning_background,(0,0))
            Screen.draw_end_screen("YOU WON!")
            won_button.draw(screen)
        
            if previous_gamemode == "easy" and not medium_just_unlocked:
                medium_unlocked = True
                medium_unlocked_counter += 1
                medium_just_unlocked = True 
        
            if previous_gamemode == "medium" and not hard_just_unlocked:
                hard_unlocked = True
                hard_unlocked_counter += 1
                hard_just_unlocked = True
        
            if medium_unlocked_counter == 1 and previous_gamemode == "easy":
                Screen.draw_unlocked("You unlocked game mode medium!")
            if hard_unlocked_counter == 1  and previous_gamemode == "medium":
                Screen.draw_unlocked("You unlocked game mode hard!")
                
        else:
            screen.blit(lost_background,(0,0))
            Screen.draw_end_screen("YOU LOST!")
            lost_button.draw(screen)
        
        if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or won_button.clicked(event) or lost_button.clicked(event):  
            game_state = "gamemode"
            medium_just_unlocked = False
            hard_just_unlocked = False
            
            # nieuwe walls and bushes generaten bij een nieuwe game
            list_of_objects.clear()
            available_positions = Screen.available_positions()
            walls = GenerateObject(wall_amount ,  Wall,wall_image,player,bot1_start_pos,bot2_start_pos)
            walls.generate()
            bushes = GenerateObject( bush_amount , Bush,bush_image,player,bot1_start_pos,bot2_start_pos)
            bushes.generate()
            
        if keys[pygame.K_i] or instructions_button.clicked(event):
            game_state = "instructions"


    # exiting
    if keys[pygame.K_ESCAPE]:
        running = False
    
    pygame.display.update()

pygame.quit()
