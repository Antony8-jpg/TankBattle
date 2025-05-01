import pygame
import math
import random
from pygame import mixer
import heapq # voor de grid

# TO DO:
#bot movement: a-star op bepaalde momenten 
#power ups
#verschillende soorten kogels en interacties met de walls of bushes
#meerdere bots met verschillende eigenschappen 


pygame.init()
clock = pygame.time.Clock()
current_time = pygame.time.get_ticks()        
last_print_time = 0

screen_length = 1100
screen_height = 650
player_size = [40,40]
bot_size = [40,40]
grid_size = 35

# background
screen = pygame.display.set_mode((screen_length,screen_height))
unsized_background = pygame.image.load("plains.jpg")
background = pygame.transform.scale(unsized_background,(screen_length,screen_height))
pygame.display.set_caption("Tank Battle")
icon = pygame.image.load("tank_icon.png")
pygame.display.set_icon(icon)
mixer.music.load("background.wav")
mixer.music.play(-1)
mixer.music.set_volume(0.5)
hit_sound = mixer.Sound("hit_sound.ogg")
hit_sound.set_volume(1.0)
                    
# grid
grid_length = screen_length // grid_size
grid_height = screen_height // grid_size

#player
unsized_player = pygame.image.load("new_tank_image.png")
player_image = pygame.transform.scale(unsized_player,(player_size[0],player_size[1]))
player_pos = pygame.math.Vector2(100, screen_height / 2)
direction = pygame.math.Vector2(1,1)
player_speed = 10
rotation_speed = 15
angle = 0
player_health = 5


# bot 
unsized_bot = pygame.image.load("enemytank_image.png")
bot_image = pygame.transform.scale(unsized_bot,(bot_size[0],bot_size[1]))
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
unsized_bullet = pygame.image.load("bullet_image1.png")
bullet_image = pygame.transform.scale(unsized_bullet, (bullet_size[0],bullet_size[1]))
bullet_cooldown = 2000
ammo_pos = [10,70]
max_ammo = 3

#special bullet
unsized_special_bullet = pygame.image.load("bullet_special.png")
special_bullet_image = pygame.transform.scale(unsized_special_bullet, (bullet_size[0], bullet_size[1]))

#wall
wall_size = [35,35]
unsized_wall = pygame.image.load("brick_wall.png")      
wall_image = pygame.transform.scale(unsized_wall, (wall_size[0],wall_size[1]))
wall_amount = 15

#bush
bush_size = [35,35]
unsized_bush = pygame.image.load("bush.png")
bush_image = pygame.transform.scale(unsized_bush, (bush_size[0],bush_size[1]))
bush_amount = 15

#heart
playerheart_size = [50,50]
botheart_size = [15,15]
unsized_heart = pygame.image.load("heart.png")
playerheart_image = pygame.transform.scale(unsized_heart,(playerheart_size[0],playerheart_size[1]))
botheart_image = pygame.transform.scale(unsized_heart,(botheart_size[0],botheart_size[1]))
heart_pos = [10,10]

#shield
playershield_size = [50,50]
botshield_size = [15,15]
shield_size =  [35,35]
unsized_shield = pygame.image.load("shield.png")
playershield_image = pygame.transform.scale(unsized_shield,(playershield_size[0],playershield_size[1]))
botshield_image = pygame.transform.scale(unsized_shield,(botshield_size[0],botshield_size[1]))
shield_image = pygame.transform.scale(unsized_shield,(shield_size[0],shield_size[1]))
next_shield_time = pygame.time.get_ticks() + random.randint(10000, 30000)
shield = None #er kan tegelijk maar 1 shield in de game zijn, in het begin geen shield

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
        self.speed = player_speed
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
        
    def player_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.speed = player_speed
        elif keys[pygame.K_DOWN]:
            self.speed = -player_speed
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
    def __init__(self, pos,bot_image,bot_speed,bot_angle):
        super().__init__(pos)
        self.image = bot_image
        self.rect = self.image.get_rect(center = self.pos)
        self.speed = bot_speed
        self.angle = bot_angle
        self.last_shot_time = 0
        self.state = "follow"
        self.state_starttime = pygame.time.get_ticks()
        self.state_duration = random.randint(2000, 4000)
        self.last_moved_time = pygame.time.get_ticks()
        self.direction = pygame.math.Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize()
        self.last_position = self.pos.copy()
        self.last_path_update_time = pygame.time.get_ticks()
        self.health = 5
        self.has_shield = False
        self.path = []
        
    def update_state(self):
        current_time = pygame.time.get_ticks()

        # Detect if stuck
        movement_threshold = 1.5
        time_since_last_check = current_time - self.last_moved_time

        if time_since_last_check > 500:
            if self.pos.distance_to(self.last_position) < movement_threshold:
                self.state = "follow"
                self.path = []  # force new path
            else:
                self.last_position = self.pos.copy()
            self.last_moved_time = current_time

        # Time-based state switch
        if current_time - self.state_starttime > self.state_duration:
            self.state = random.choice(["random", "follow"])
            self.state_duration = random.randint(2000, 4000)
            self.state_starttime = current_time

            if self.state == "random":
                self.angle = random.randint(0, 360)
                self.direction = pygame.math.Vector2(
                    math.cos(math.radians(self.angle + 90)),
                    -math.sin(math.radians(self.angle + 90))
                )

        # === FOLLOW STATE ===
        if self.state == "follow":
            if current_time - self.last_path_update_time > 300 or not self.path:
                grid = Grid.build_grid()
                start = Grid.screen_to_grid(self.pos)
                goal = Grid.screen_to_grid(player.pos)
                new_path = Grid.astar(start, goal, grid)

                if new_path:
                    self.path = new_path
                else:
                    self.state = "random"
                    self.state_starttime = current_time
                    self.state_duration = random.randint(2000, 4000)
                    self.angle = random.randint(0, 360)
                    self.direction = pygame.math.Vector2(
                        math.cos(math.radians(self.angle + 90)),
                        -math.sin(math.radians(self.angle + 90))
                    )
                    return

                self.last_path_update_time = current_time

            if self.path:
                next_step = Grid.grid_to_screen(self.path[0])
                if self.pos.distance_to(next_step) < 5:
                    self.path.pop(0)
                if self.path:
                    next_step = Grid.grid_to_screen(self.path[0])
                    self.direction = (next_step - self.pos).normalize()
                    self.angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90



    def bot_movement(self,lengte,hoogte):
        self.pos += self.speed * self.direction
        # om niet te laggen
        distance = self.pos.distance_to(player.pos)
        if distance < 100:
            self.speed = 0
            
        else:
            self.speed = bot_speed
        
        self.pos.x = max(0, min(self.pos.x, lengte))
        self.pos.y = max(0, min(self.pos.y, hoogte))

        rotated_bot_image = pygame.transform.rotate(self.image,self.angle)
        self.rect = rotated_bot_image.get_rect(center = self.pos)
        return rotated_bot_image, self.rect
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > bot_shooting_speed:
            self.last_shot_time = current_time
            self.direction = pygame.math.Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize() #richting nog eens updaten zodat kogel juist georiënteerd is
            self.angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90
            bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
            bullet_list_bot.append(bullet)

    def move_random(self):
        pass #nog aanvullen

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

class Shield(StationaryObject):
    def __init__(self, pos, image):
        super().__init__(pos)
        self.image = image
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

class Wall(StationaryObject):
    def __init__(self,pos, wallIMG):
        super().__init__(pos)
        self.image = wallIMG
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

class Bush(StationaryObject):
    def __init__(self,pos, bushIMG):
        super().__init__(pos)
        self.image = bushIMG
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
    
    def draw(self):
        screen.blit(self.image, self.rect.topleft)

class Figure(Object):
    def __init__(self,pos):
        super().__init__(pos)

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
    
    def print_ammo(ammo_pos,bullet_image,player_ammo,spacing = bullet_size[0]):
        for i in range(player_ammo):
            screen.blit(bullet_image,(ammo_pos[0]+i*spacing,ammo_pos[1]))
            
    def draw_special_bullet_ammo(player, position=(10, 120)):
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
    
    def line_grids(start_pos, end_pos, grid_size):
        grids = []
        list_of_obstacles = []
        current_time = pygame.time.get_ticks()
        global last_print_time
        
        # zet alle grids waardoor de verbindingslijn gaat in een lijst
        stappen = 100
        for i in range(stappen + 1):
            t = i / stappen
            x = start_pos.x + (end_pos.x - start_pos.x) * t
            y = start_pos.y + (end_pos.y - start_pos.y) * t
            grid_x = int(x) // grid_size
            grid_y = int(y) // grid_size
            grid = (grid_x, grid_y)
            if grid not in grids: # om geen dubbele te hebben
                grids.append(grid)
        # teken de grids
        for grid in grids:
            # grids tekenen
            x = grid[0] * grid_size
            y = grid[1] * grid_size
            pygame.draw.rect(screen, (255, 255, 255), (x, y, grid_size, grid_size), 2)
            # obstacles bijhouden (obstacles -> objecten die in de weg staan)
            for object in list_of_objects:
                if (grid[0],grid[1]) == (object.grid_x,object.grid_y):
                    list_of_obstacles.append([object.grid_x,object.grid_y])
        
        # timer om te printen anders is het veel
        if current_time - last_print_time > 1000:
            print(list_of_obstacles)
            last_print_time = current_time
        return

    def screen_to_grid(pos):
        return (int(pos.x) // grid_size, int(pos.y) // grid_size)

    def grid_to_screen(grid_pos):
        return pygame.math.Vector2((grid_pos[0] + 0.5) * grid_size, (grid_pos[1] + 0.5) * grid_size)

    def build_grid(): # maak een de map een grid van nullen en 1 , 0 als vrij en 1 als er een obstacle is
        grid = []
        for i in range(grid_length): # maakt een lijst van nullen 
            row = [0] * grid_height
            grid.append(row)

        for obj in list_of_objects: # vervangt de 0 door een 1 als er een obstacle is
            if isinstance(obj, (Wall, Bush)):
                grid[obj.grid_x][obj.grid_y] = 1

        return grid
    
    def heuristic(a, b): # geeft een waarde (f_score) voor de afstand tot het doel -> van chatgpt
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def is_area_clear(grid, x, y, clearance):  # om een vrije 3x3 gebied te vinden zodat de bot zeker door kan gaan (zou kunnen botsen tegen zijkant als 1x1) -> aangepaste versie van chatgpt
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

    def astar(start_cell, goal_cell, grid):
        from heapq import heappush, heappop

        # priority queue van estimated_total_cost, cel
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
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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
                is_walkable = Grid.is_area_clear(grid, neighbor_x, neighbor_y, clearance=1)
                if not is_walkable:
                    continue

                # temporary cost van start tot neighbor
                temporary_cost = cost_from_start[current_cell] + 1

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

class Rectangle(Figure):
    def __init__(self, pos, color, width, height):
        super().__init__(pos)
        self.color = color
        self.width = width
        self.height = height
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

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
list_of_objects = []
available_positions = [
    (x, y)
    for x in range(wall_size[0]//2, screen_length - wall_size[0]//2, wall_size[0])
    for y in range(wall_size[1]//2, screen_height - wall_size[1]//2, wall_size[1])
] 

walls = GenerateObject(amount= wall_amount , object= Wall, image = wall_image)
walls.generate()
bushes = GenerateObject(amount= bush_amount , object= Bush, image= bush_image)
bushes.generate()


#game state op running zetten en welk lettertype tekst
game_state = "start"  #verschillende states: "start", "instructions", "running", "won", "lost"
font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 50)

#gameloop
running = True
while running:
    clock.tick(20)
    screen.blit(background,(0,0))
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
        previous_pos = player.pos.copy()
        player.player_movement()  
        rotated_image, player_rect = player.update(screen_length, screen_height)
        player.shoot()
        player.shoot_special()
        player.reload_ammo()
        player_grid_pos = player.player_grid_pos() # dient voor niks denk ik
        
        previous_bot_pos = bot.pos.copy()
        rotated_bot_image,bot_rect = bot.bot_movement(screen_length,screen_height)
        bot.shoot()
        bot.update_state()

        #shields spawnen
        current_time = pygame.time.get_ticks()
        if current_time >= next_shield_time and shield is None: #als interval gedaan is en er is geen shield in de game 
            random.shuffle(available_positions) #lijst random door elkaar shuffelen 
            
            for (x, y) in available_positions: #positie zoeken voor het shield
                new_pos = pygame.math.Vector2(x, y)
                
                shield_safe_to_spawn = True
                for obj in list_of_objects: #extra controleren of shield zeker niet op een wall of bush staat
                    if obj.rect.collidepoint(x, y):
                        shield_safe_to_spawn = False
                        break
                    
                if new_pos.distance_to(player.pos) > 100 and new_pos.distance_to(bot.pos) > 100 and shield_safe_to_spawn: #shield ook niet te dicht bij player en bot
                    shield = Shield((x, y), shield_image)
                    break
                
            next_shield_time = current_time + random.randint(10000, 30000)
        
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
             
        #collision shield and player/bot
        if shield:
            if player.rect.colliderect(shield.rect):
                player.has_shield = True
                shield = None
            elif bot.rect.colliderect(shield.rect):
                bot.has_shield = True
                shield = None
     
        #walls en bushes tekenen 
        for object in list_of_objects:
            if hasattr(object, "draw"):
                object.draw()
                
        #shield tekenen: als er een shield is moet deze getekend worden
        if shield:
            shield.draw() 
            
                        
        # levens en ammo tekenen
        Screen.player_hearts(heart_pos,player.health,playerheart_image)
        Screen.bot_hearts(previous_bot_pos,bot.health,botheart_image)
        Screen.print_ammo(ammo_pos,bullet_image,player.ammo)
        Screen.draw_special_bullet_ammo(player)
        Screen.draw_reload_timer(player)
        Screen.draw_shield_indicator(player, bot)
        player_rect = MovingObject.blit_rotated_image(screen, player.image, player.pos, player.angle, player_size)
        bot_rect = MovingObject.blit_rotated_image(screen, bot.image, bot.pos, bot.angle, bot_size)

        #rect tekenen om collision te begrijpen
        pygame.draw.rect(screen, (255, 0, 0), player_rect, 2)
        pygame.draw.rect(screen, (0, 0, 255), bot_rect, 2)
        # pygame.draw.line(screen,(255,0,0),bot.pos,player.pos)
        # grids = Grid.line_grids(player.pos, bot.pos, grid_size)
        

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
        shield = None
        player.has_shield = False
        bot.has_shield = False
        next_shield_time = pygame.time.get_ticks() + random.randint(10000, 30000)
        
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
