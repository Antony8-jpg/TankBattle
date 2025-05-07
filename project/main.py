import pygame

# import files
from Variabels import *
from ScreenObjects import *
from Powerups import *
from MovingObjects import *

import pygame
import math
import random
from queue import PriorityQueue

# TO DO:
# meerdere bots
# in meerdere files zetten

pygame.init()
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()        
last_print_time = 0

class Player(MovingObject):
    def __init__(self,pos,direction,player_speed,rotation_speed,angle,playerImg):
        super().__init__(pos)
        self.direction = direction
        self.rotation_speed = rotation_speed
        self.angle = angle
        self.image = playerImg
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size[0], player_size[1])
        self.last_shot_time = 0 #timer voor bullets    
        self.ammo = 3
        self.last_reload_time = pygame.time.get_ticks()
        self.health = 5
        self.has_special_bullet = True
        self.has_shield = False
        self.speed_boost_active = False
        self.speed_boost_start_time = 0
        self.base_speed = player_speed

    def player_movement(self):
        #speed updaten en powerup checken
        if self.speed_boost_active and pygame.time.get_ticks() - self.speed_boost_start_time > speed_boost_duration:
            self.speed_boost_active = False
        
        actual_speed = self.base_speed * (1.5 if self.speed_boost_active else 1)
        
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
            
    def player_grid_pos(self):  # dient voor niks denk ik 
        grid_x = int(self.pos.x)//grid_size
        grid_y = int(self.pos.y)//grid_size
        return grid_x,grid_y
    
    def reset(self):
        self.health = 5
        self.ammo = max_ammo
        self.has_special_bullet = True
        self.direction = pygame.math.Vector2(0, 1)
        self.pos = pygame.math.Vector2(100, screen_height / 2)
        self.angle = 0
        self.has_shield = False
        self.speed_boost_active = False
        self.speed_boost_start_time = 0

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

class Grid:
    def screen_to_grid(pos): 
        return (int(pos.x) // grid_size, int(pos.y) // grid_size)

    def grid_to_screen(grid_pos):
        return pygame.math.Vector2((grid_pos[0] + 0.5) * grid_size, (grid_pos[1] + 0.5) * grid_size)

    def build_grid(): # maak een de map een grid van nullen en 1 , 0 als vrij en 1 als er een obstacle is
        grid = []
        for i in range(grid_length): # verandert elke cel in een 0 
            row = [0] * grid_height 
            grid.append(row)

        for obj in list_of_objects: # vervangt de 0 door een 1 als er een obstacle is
            if isinstance(obj, (Wall, Bush)):
                grid[obj.grid_x][obj.grid_y] = 1

        return grid
    
    def heuristic(a, b): #Manhatten distance tussen twee punten a an b
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clear_area(grid, x, y, clearance):  # om een vrije 3x3 gebied te vinden zodat de bot zeker door kan gaan (zou kunnen botsen tegen zijkant als 1x1)
        grid_width = len(grid)
        grid_height = len(grid[0])
        
        # gaat loopen over elke grid in nabijheid bot (3x3) als die vrij is of niet, clearance zal =1 zijn bij oproepen van functie
        for dx in range(-clearance, clearance + 1):
            for dy in range(-clearance, clearance + 1):
                check_x = x + dx
                check_y = y + dy

                # overslaan als de cel buiten de grid is
                if check_x < 0 or check_x >= grid_width:
                    return False
                if check_y < 0 or check_y >= grid_height:
                    return False

                # checken als obstacle op de grid
                if grid[check_x][check_y] == 1:
                    return False

        # alle andere grids zijn dan vrij -> True
        return True

    def astar(start_cell, goal_cell, grid): # code van chatgpt, pathfinding langs vrije pad
        #priority queue aanmaken en start_cell toevoegen met priority 0
        open_cells = PriorityQueue()
        open_cells.put((0, start_cell))

        #dict om het pad bij te houden via backtracking 
        came_from = {}
        #de kost om van start tot huidige cell te gaan
        cost_from_start = {start_cell: 0}

        #loopen over alle open cellen
        while not open_cells.empty():
            #beginnen met de cell met de kleinste estimated_total_cost
            current_priority, current_cell = open_cells.get()

            #doel bereikt -> maak het pad via backtracking
            if current_cell == goal_cell:
                path = []
                while current_cell in came_from:
                    path.append(current_cell)
                    current_cell = came_from[current_cell]
                path.reverse() #pad moet nog omgedraaid worden
                return path

            #alle mogelijke richtingen: horizontaal, verticaal en diagonaal
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction_x, direction_y in directions:
                neighbour_x = current_cell[0] + direction_x
                neighbour_y = current_cell[1] + direction_y
                neighbour_cell = (neighbour_x, neighbour_y)

                #begin opnieuw als de cel buiten het veld is
                if neighbour_x < 0 or neighbour_x >= grid_length:
                    continue
                if neighbour_y < 0 or neighbour_y >= grid_height:
                    continue

                #begin opnieuw als de cel ernaast niet vrij is
                is_walkable = Grid.clear_area(grid, neighbour_x, neighbour_y, clearance=1)
                if not is_walkable:
                    continue
                
                #voorkomen dat je diagonaal door obstakels gaat
                if abs(direction_x) == 1 and abs(direction_y) == 1: #diagonale beweging, vb: (2,2) -> (3,3)
                    if grid[neighbour_x][current_cell[1]] == 1 or grid[current_cell[0]][neighbour_y] == 1: #1 = obstakel
                        continue  

                #de kost van de stap bepalen: 1 voor recht, sqrt(2) voor diagonaal en de kost updaten
                step_cost = math.sqrt(2) if abs(direction_x) + abs(direction_y) == 2 else 1
                new_cost = cost_from_start[current_cell] + step_cost

                #als deze route goedkoper is dan een eerder gevonden pad naar deze cel
                if neighbour_cell not in cost_from_start or new_cost < cost_from_start[neighbour_cell]:
                    came_from[neighbour_cell] = current_cell #update het pad
                    cost_from_start[neighbour_cell] = new_cost #kost van het pad updaten

                    #Bereken de prioriteit met behulp van de manhatten distance en voeg toe aan de queue
                    priority = new_cost + Grid.heuristic(neighbour_cell, goal_cell)
                    open_cells.put((priority, neighbour_cell))

        #Indien geen pad gevonden wordt 
        return None

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
