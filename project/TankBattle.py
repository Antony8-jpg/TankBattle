import pygame
import math
import random
from pygame import mixer

# TO DO:
# startscreen met knoppen
# meerdere bots
# in meerdere files zetten

pygame.init()
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()        
last_print_time = 0

class GameImage:
    def __init__(self, name, size):
        self.name = name
        self.size = size 
        self.image = self.load_scaled_image()
        
    def load_scaled_image(self):
        unsized_image = pygame.image.load(self.name)
        return pygame.transform.scale(unsized_image , self.size)

# background
screen_size = [1100, 650]
screen_length = screen_size[0] #makkelijker om screen height en lenght verder te gebruiken
screen_height = screen_size[1]
screen = pygame.display.set_mode((screen_length,screen_height))
game_background = GameImage("plains.jpg", screen_size).image
main_background = GameImage("main_background.jpg", screen_size).image
pygame.display.set_caption("Tank Battle")
icon = pygame.image.load("tank_icon.png")
pygame.display.set_icon(icon)
mixer.music.load("background.wav")
mixer.music.play(-1)
mixer.music.set_volume(0.5)
hit_sound = mixer.Sound("hit_sound.ogg")
hit_sound.set_volume(1.0)
                    
# grid
grid_size = 35
grid_length = screen_length // grid_size
grid_height = screen_height // grid_size

#player
player_size = [40,40]
player_image = GameImage("new_tank_image.png", player_size).image
player_pos = pygame.math.Vector2(100, screen_height / 2)
direction = pygame.math.Vector2(1,1)
player_speed = 10
rotation_speed = 15
angle = 0
player_health = 5

# bot 
bot_size = [40,40]
bot_image = GameImage("enemytank_image.png", bot_size).image
bot_pos = pygame.math.Vector2(screen_length -100 , screen_height/2)
bot_speed = 3
bot_angle = 0
bot_rotation_speed = rotation_speed
bot_shooting_speed = 2000
bot_health = 5

#bullet
bullet_size = [10,25]
bullet_speed = 20
bullet_list_player = []
bullet_list_bot = []
bullet_image = GameImage("bullet_image1.png", bullet_size).image
bullet_cooldown = 2000
ammo_pos = [10,70]
max_ammo = 3

#special bullet
special_bullet_image = GameImage("bullet_special.png", bullet_size).image

#wall
wall_size = [35,35]
wall_image = GameImage("brick_wall.png", wall_size).image
wall_amount = 15

#bush
bush_size = [35,35]
bush_image = GameImage("bush.png", bush_size).image
bush_amount = 15

#heart
playerheart_size = [50,50]
botheart_size = [15,15]
playerheart_image = GameImage("heart.png", playerheart_size).image
botheart_image = GameImage("heart.png", botheart_size).image
heart_pos = [10,10]

#powerups 
active_powerups = [] #lijst die gebruikt wordt zodat powerups niet op dezelfde plaats kunnen spawnen
playershield_size = [50,50]
botshield_size = [15,15]
powerup_size =  [35,35]
playershield_image = GameImage("shield.png", playershield_size).image
botshield_image = GameImage("shield.png", botshield_size).image
shield_image = GameImage("shield.png", powerup_size).image 
shield_timer_active = False
next_shield_time = 0  #wordt later geüpdated
shield = None #er kan tegelijk maar 1 shield in de game zijn, in het begin geen shield
speed_boost_image = GameImage("speed_boost.png", powerup_size).image
speed_boost_duration = 10000 #10 s

#classes
class Object:
    def __init__(self,pos):
        self.pos = pos
    
    def collision(self, otherObject):
    # Controleer of beide objecten een rect attribuut hebben
        if hasattr(self, 'rect') and hasattr(otherObject, 'rect'):
            return self.rect.colliderect(otherObject.rect) #geeft True bij botsing, False bij geen botsing
        return False  # Als een van de objecten geen rect heeft, return False
        
class MovingObject(Object):
    def __init__(self,pos):
        super().__init__(pos)
        
    def manage(self, bullet_list , yourobject, other_object):
        for bullet in bullet_list[:]: #kopie van de lijst gebruiken om veilig bullets te verwijderen
            if not bullet.launch(): #als launch False geeft
                bullet_list.remove(bullet)
            else:
                rotated_bullet = pygame.transform.rotate(bullet.image, bullet.angle)  #kogel wordt geroteerd
                screen.blit(rotated_bullet, bullet.rect.topleft)
                
                for object in list_of_objects:
                    if bullet.collision(object):
                        if isinstance(object, Wall) and isinstance(bullet, SpecialBullet):
                            list_of_objects.remove(object)  # SpecialBullet detroyed walls
                        elif isinstance(object, Bush):
                            list_of_objects.remove(object)
                        bullet_list.remove(bullet)
                        break  # voorkomt dubbele verwijdering van een bullet bij 2 collisions
                
                if bullet not in bullet_list:  #Als de bullet al verwijderd is, niet verder checken
                    continue 
                        
                if bullet.collision(other_object):
                    bullet_list.remove(bullet)
                    if hasattr(other_object, 'has_shield') and other_object.has_shield:
                        other_object.has_shield = False  # Shield verliest bescherming
                        
                    else:
                        damage = 2 if isinstance(bullet, SpecialBullet) else 1
                        other_object.health -= damage
                        hit_sound.play()
                    break

    def blit_rotated_image(surf, image, center_pos, angle, true_rect_size):
        # roteer de image
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=center_pos)

        # teken de geroteerde afbeelding
        surf.blit(rotated_image, rotated_rect.topleft)

        # true_rect voor de rectangle die niet roteert, deze wordt gebruikt voor collisions ...
        true_rect = pygame.Rect(
            center_pos[0] - true_rect_size[0] // 2,
            center_pos[1] - true_rect_size[1] // 2,
            true_rect_size[0],
            true_rect_size[1]
            )

        return true_rect

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
        if self.speed_boost_active and pygame.time.get_ticks() - self.speed_boost_start_time > 10000:
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
        self.start = Grid.screen_to_grid(self.pos) # startpositie van de bot

        # als er een shield is gaat de bot ervoor (1 kans op 3)
        shield_targeted = False
        if shield_spawner.powerup and self.state != "shield": #shield state toevoegen om niet 2 shields te hebben
            if random.randint(1, 3) == 1:
                self.goal = Grid.screen_to_grid(pygame.math.Vector2(shield_spawner.powerup.rect.center))
                self.state = "shield" 
                self.state_starttime = current_time 
                self.state_duration = random.randint(3000, 5000) # gaat naar de shield enkel voor 4 seconden (om te voorkomen dat hij geblokkeerd is als hij zijn pad niet vindt)
                print("going for shield")
                shield_targeted = True

        # state update
        if self.state != "shield" and current_time - self.state_starttime > self.state_duration:
            self.state_starttime = current_time
            self.state_duration = random.randint(2000, 4000)

            if self.pos.distance_to(player.pos) < 250: # volgt de player als die dichtbij is
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

        # pad volgen
        if self.path:
            next_step = Grid.grid_to_screen(self.path[0])
            if self.pos.distance_to(next_step) < 5:
                self.path.pop(0) # haal het eerste element eruit
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
                    # zoekt een open plek rond de player
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


class Bullet(MovingObject):
    def __init__(self, pos, direction, speed, angle, bulletIMG):
        super().__init__(pos)
        self.direction = direction
        self.speed = speed
        self.angle = angle
        self.image = bulletIMG
        self.rect = self.image.get_rect(center = self.pos)
            
    
    def launch(self):
        self.pos += self.speed * self.direction 
        self.rect.center = self.pos
        rotated_bullet = pygame.transform.rotate(self.image, -self.angle)
        self.rect = rotated_bullet.get_rect(center = self.pos)
        
        
        if self.pos.x < 0 or self.pos.x > screen_length or self.pos.y < 0 or self.pos.y > screen_height:
           return False  # Geeft False om bullet te verwijderen uit de bullet lijst
        return True  # Bullet blijft in de lijst
        
class SpecialBullet(Bullet):
    def __init__(self, pos, direction, speed, angle, bulletIMG):
        super().__init__(pos, direction, speed, angle, bulletIMG)
        
    def launch(self):
        return super().launch()

class StationaryObject(Object):
    def __init__(self,pos):
        super().__init__(pos)
        self.grid_x = int(self.pos[0]) // grid_size
        self.grid_y = int(self.pos[1]) // grid_size

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

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
    def __init__(self, powerup_class, image, player, bot, list_of_objects, available_positions, condition_func):
        self.powerup_class = powerup_class
        self.image = image
        self.player = player
        self.bot = bot
        self.list_of_objects = list_of_objects
        self.available_positions = available_positions
        self.condition_func = condition_func  #dit is een functie die nodig is om voorwaarden te checken, maar die verschillend is voor elke powerup bv. not player.has_shield
        self.powerup = None
        self.next_spawn_time = 0
        self.timer_active = False


    def update(self):
        current_time = pygame.time.get_ticks()

        #tijdsinterval voor het spawnen van de powerup starten
        if not self.timer_active and self.powerup is None and self.condition_func(self.player): 
            self.next_spawn_time = current_time + random.randint(10000, 30000)
            self.timer_active = True

        #positie voor de powerrup zoeken
        if current_time >= self.next_spawn_time and self.powerup is None and self.condition_func(self.player):
            random.shuffle(self.available_positions) #lijst random shuffelen
            for (x, y) in self.available_positions:
                new_pos = pygame.math.Vector2(x, y)
                
                powerup_safe_to_spawn = True
                for obj in self.list_of_objects + active_powerups: #extra controleren of powerup op een veilige locatie wordt gespawnd
                    if obj.rect.collidepoint(x, y):
                        powerup_safe_to_spawn = False
                        break
                
                if new_pos.distance_to(self.player.pos) > 200 and new_pos.distance_to(self.bot.pos) > 200 and powerup_safe_to_spawn:
                    self.powerup = self.powerup_class((x, y), self.image)
                    active_powerups.append(self.powerup)
                    self.timer_active = False
                    break
        
        #collision met player
        if self.powerup and self.player.rect.colliderect(self.powerup.rect):
            self.powerup.apply_effect(self.player)
            active_powerups.remove(self.powerup)
            self.powerup = None
            
        #collision met bot (enkel voor shield)
        if self.powerup and isinstance(self.powerup, Shield) and self.bot.rect.colliderect(self.powerup.rect):
            self.powerup.apply_effect(self.bot)
            active_powerups.remove(self.powerup)
            self.powerup = None
              

    def draw(self):
        if self.powerup:
            self.powerup.draw()

    def reset(self):
        self.powerup = None
        self.timer_active = False
        self.next_spawn_time = 0

class Wall(StationaryObject):
    def __init__(self,pos, wallIMG):
        super().__init__(pos)
        self.image = wallIMG
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def draw(self):
       return super().draw()

class Bush(StationaryObject):
    def __init__(self,pos, bushIMG):
        super().__init__(pos)
        self.image = bushIMG
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
    
    def draw(self):
        return super().draw()

class Screen():
    def __init__(self,pos):
        self.pos = pos
    
    def draw_reload_timer(player):
        current_time = pygame.time.get_ticks()
        if player.ammo < max_ammo:
            time_since_reload = current_time - player.last_reload_time
            progress = min(time_since_reload / bullet_cooldown, 1.0)
            bar_width = 50
            pygame.draw.rect(screen, (255, 0, 0), (ammo_pos[0], ammo_pos[1] + 40, bar_width, 10)) # lege bar tekenen
            pygame.draw.rect(screen, (0, 255, 0), (ammo_pos[0], ammo_pos[1] + 40, progress * bar_width, 10)) # progress in bar tekenen
            
    def available_positions():
        available_positions = [
             (x, y)
             for x in range(75, screen_length - 50, wall_size[0])
             for y in range(75, screen_height - 50, wall_size[1])
         ]
        return available_positions
    
    def print_ammo(ammo_pos,bullet_image,player_ammo,spacing = bullet_size[0]):
        for i in range(player_ammo):
            screen.blit(bullet_image,(ammo_pos[0]+i*spacing,ammo_pos[1]))
            
    def draw_special_bullet_ammo(player, position=(10, 130)):
        if player.has_special_bullet:
            screen.blit(special_bullet_image, position)
    
    def player_hearts(heart_pos,player_health, heart_image,spacing = playerheart_size[0]):
        for i in range(player_health):
            screen.blit(heart_image,(heart_pos[0]+i*spacing,heart_pos[1]))
    
    def bot_hearts(bot_pos,bot_health,heart_image):
        if bot_health >0:
            spacing = bot_size[0] / bot_health
        x_waarde = bot_pos.x - bot_size[0]/2
        y_waarde = bot_pos.y - bot_size[1]
        for i in range(bot_health):
            screen.blit(heart_image,(x_waarde + i*spacing,y_waarde))
            
    def draw_shield_indicator(player, bot):
        #shield player wordt naast health getoond
        if player.has_shield:
            x = heart_pos[0] + player.health * playerheart_size[0] + 5  #rechts van de laatste hartje
            y = heart_pos[1] 
            screen.blit(playershield_image, (x, y))
    
        #shield van de bot wordt naast de hartjes van de bot getoond
        if bot.has_shield:
            spacing = bot_size[0] / max(bot.health, 1)
            bot_heart_x = bot.pos.x - bot_size[0]/2 + bot.health * spacing
            bot_heart_y = bot.pos.y - bot_size[1]
            screen.blit(botshield_image, (bot_heart_x + 5, bot_heart_y))

    def draw_speed_boost(player, position = (5, 165)):
        if player.speed_boost_active:
            screen.blit(speed_boost_image, position)
            current_time = pygame.time.get_ticks()
            time_since_start_boost = current_time - player.speed_boost_start_time
            duration = speed_boost_duration
            progress = max(0, min(1.0, 1 - time_since_start_boost / duration))  #balk gaat van 1 tot 0, max en min is zodat het altijd tussen 0 en 1 zit
            bar_width = 50
            bar_height = 10
            pygame.draw.rect(screen, (50, 50, 50), (5, 210, bar_width, bar_height)) #lege bar
            pygame.draw.rect(screen, (0, 150, 255), (5, 210, progress * bar_width, bar_height)) #progress bar

    def draw_end_screen(message):
        text = font.render(message, True, (255, 255, 255))
        subtext = small_font.render("Press R to Restart, ESC to Quit or i for instructions", True, (255, 255, 255))
        screen.blit(text, (screen_length // 2 - text.get_width() // 2, screen_height // 3))
        screen.blit(subtext, (screen_length // 2 - subtext.get_width() // 2, screen_height // 2))
        
    def draw_start_screen():
        title = font.render("Tank Battle", True, (255, 255, 255))
        subtitle = small_font.render("Press ENTER to Start or i for instructions", True, (255, 255, 255))
        screen.blit(title, (screen_length // 2 - title.get_width() // 2, screen_height // 3))
        screen.blit(subtitle, (screen_length // 2 - subtitle.get_width() // 2, screen_height // 2))
        
    def draw_instruction_screen():
        instructions = [
            "Move with arrow keys",
            "Shoot bullets with SPACEBAR",
            "Shoot special bullet with F key",
            "Hearts represent your health",
            "Defeat the enemy bot!"
        ]
        title = font.render("Instructions", True, (255, 255, 255))
        screen.blit(title, (screen_length // 2 - title.get_width() // 2, 50))
    
        for i, line in enumerate(instructions): #positie van de tekst en de lijn bijhouden
            line_render = small_font.render(line, True, (255, 255, 255))
            screen.blit(line_render, (screen_length // 2 - line_render.get_width() // 2, 150 + i * 60)) #positie van de tekst bepalen
    
        subtext = small_font.render("Press BACKSPACE to return to title screen or ENTER to start", True, (255, 255, 255))
        screen.blit(subtext, (screen_length // 2 - subtext.get_width() // 2, screen_height - 100))

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
    
    def heuristic(a, b): # geeft een waarde (f_score) voor de afstand tot het doel -> van chatgpt
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
        from heapq import heappush, heappop

        # priority queue van estimated_total_cost
        open_cells = []
        heappush(open_cells, (0, start_cell))

        # om het beste path bij te houden
        came_from = {}

        # om de "kost" van het pad bij te houden
        cost_from_start = {start_cell: 0}

        # loopen over alle open cellen
        while open_cells:
            # beginnen met de cell met de kleinste estimated_total_cost
            current_priority, current_cell = heappop(open_cells)

            # doel bereikt -> maak het pad in backtracking
            if current_cell == goal_cell:
                path = []
                while current_cell in came_from:
                    path.append(current_cell)
                    current_cell = came_from[current_cell]
                path.reverse()
                return path

            # definieer alle mogelijke richtingen : up, down, left, right
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for direction_x, direction_y in directions:
                neighbor_x = current_cell[0] + direction_x
                neighbor_y = current_cell[1] + direction_y
                neighbor_cell = (neighbor_x, neighbor_y)

                # skip als de cel ernaast buiten het veld is
                if neighbor_x < 0 or neighbor_x >= grid_length:
                    continue
                if neighbor_y < 0 or neighbor_y >= grid_height:
                    continue

                # skip als de cel ernaast niet "walkable" is
                is_walkable = Grid.clear_area(grid, neighbor_x, neighbor_y, clearance=1)
                # Prevent diagonal corner cutting
                if abs(direction_x) == 1 and abs(direction_y) == 1:
                    if grid[neighbor_x][current_cell[1]] == 1 or grid[current_cell[0]][neighbor_y] == 1:
                        continue  # Can't move diagonally past a corner
                if not is_walkable:
                    continue

                # temporary cost van start tot neighbor, 1,41 voor diagonaal, 1 voor rechte lijn
                step_cost = math.sqrt(2) if abs(direction_x) + abs(direction_y) == 2 else 1
                
                temporary_cost = cost_from_start[current_cell] + step_cost

                # als deze pad beter is dan de vorige
                if neighbor_cell not in cost_from_start or temporary_cost < cost_from_start[neighbor_cell]:
                    came_from[neighbor_cell] = current_cell
                    cost_from_start[neighbor_cell] = temporary_cost

                    # estimate total cost door heuristic
                    estimated_remaining_cost = Grid.heuristic(neighbor_cell, goal_cell)
                    estimated_total_cost = temporary_cost + estimated_remaining_cost

                    # neighbor toevoegen aan de queue
                    heappush(open_cells, (estimated_total_cost, neighbor_cell))

        # If we exhaust all options without reaching the goal, return None
        return None

#klasse met een methode om walls en bushes aan te maken op random posities 
class GenerateObject: 
    def __init__(self, amount, object, image):
        self.amount = amount
        self.object = object
        self.image = image
    
    def generate(self):
        for i in range(self.amount):
            while True:
                x, y = random.choice(available_positions)
                object_pos = pygame.math.Vector2(x, y)
                
                if object_pos.distance_to(player.pos) > 2*player_size[0] and object_pos.distance_to(bot.pos) > 2*bot_size[0]:
                    wall = self.object((x, y), self.image)
                    list_of_objects.append(wall)
                    available_positions.remove((x, y))
                    break 

#objects
player = Player(player_pos, direction, player_speed, rotation_speed, angle,player_image)
bot = Bot(bot_pos,bot_image,bot_speed,bot_angle)

#walls and bushes generaten
list_of_objects = [] #walls en bushes worden in deze lijst geplaatst
available_positions = Screen.available_positions()
walls = GenerateObject(amount= wall_amount , object= Wall, image = wall_image)
walls.generate()
bushes = GenerateObject(amount= bush_amount , object= Bush, image= bush_image)
bushes.generate()

#powerups aanmaken
shield_spawner = PowerUpSpawner(Shield, shield_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.has_shield and not bot.has_shield)
special_bullet_spawner = PowerUpSpawner(SpecialBulletPickup, special_bullet_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.has_special_bullet)
speedboost_spawner = PowerUpSpawner(SpeedBoost, speed_boost_image, player, bot, list_of_objects, available_positions, condition_func = lambda x: not x.speed_boost_active)

#game state op start zetten en welk lettertype tekst
game_state = "start"  #verschillende states: "start", "instructions", "running", "won", "lost"
font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 50)

#gameloop
running = True
while running:
    clock.tick(20)
    if game_state == "running":    
        screen.blit(game_background,(0,0))
    else:
        screen.blit(main_background, (0,0))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if game_state == "start":
        Screen.draw_start_screen()
        if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:  
            game_state = "running"
        if keys[pygame.K_i]:
            game_state = "instructions"
            
    elif game_state == "instructions":
        Screen.draw_instruction_screen()
        if keys[pygame.K_BACKSPACE]:
            game_state = "start"
        if keys[pygame.K_KP_ENTER]:  
            game_state = "running"
    
    
    elif game_state == "running":
        
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
        # reset alles
        player.health = 5
        bot.health = 5
        player.ammo = max_ammo
        player.has_special_bullet = True
        player.direction = pygame.math.Vector2(0, 1)
        bot.direction = pygame.math.Vector2(0, -1)
        player.pos = pygame.math.Vector2(100, screen_height / 2)
        bot.pos = pygame.math.Vector2(screen_length - 100, screen_height / 2)
        player.angle = 0
        bullet_list_player.clear()
        bullet_list_bot.clear()
        shield_spawner.reset()
        special_bullet_spawner.reset()
        player.has_shield = False
        bot.has_shield = False
        active_powerups.clear()
        player.speed_boost_active = False
        player.speed_boost_start_time = 0
        
        #walls and bushes generaten
        list_of_objects.clear()
        available_positions = Screen.available_positions()
        walls = GenerateObject(amount= wall_amount , object= Wall, image = wall_image)
        walls.generate()
        bushes = GenerateObject(amount= bush_amount , object= Bush, image= bush_image)
        bushes.generate()
        
        if game_state == "won":
            Screen.draw_end_screen("YOU WON!")
        else:
            Screen.draw_end_screen("YOU LOST!")

        
        if keys[pygame.K_r] or keys[pygame.K_KP_ENTER]:  
            game_state = "running"
            
        if keys[pygame.K_i]:
            game_state = "instructions"


    # exiting
    if keys[pygame.K_ESCAPE]:
        running = False
    
    pygame.display.update()

pygame.quit()
