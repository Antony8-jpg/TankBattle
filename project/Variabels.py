import pygame
from pygame import mixer

pygame.init()
pygame.mixer.init()

# klasse om afbeeldingen in te laden met de juiste grootte
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
screen_length = screen_size[0] # makkelijker om screen height en lenght verder te gebruiken
screen_height = screen_size[1]
screen = pygame.display.set_mode((screen_length,screen_height))
game_background = GameImage("plains.jpg", screen_size).image
main_background = GameImage("main_background.jpg", screen_size).image
winning_background = GameImage("winning_background.jpg", screen_size).image
lost_background = GameImage("lost_background.jpg", screen_size).image
pygame.display.set_caption("Tank Battle")
icon = pygame.image.load("tank_icon.png")
pygame.display.set_icon(icon)
mixer.music.load("background.wav")
mixer.music.play(-1)
mixer.music.set_volume(0.5)
hit_sound = mixer.Sound("hit1.mp3")
hit_sound.set_volume(1.0)
kill_sound = mixer.Sound("bongo-hit.mp3")   
kill_sound.set_volume(3.0)

# grid
grid_size = 40
grid_length = screen_length // grid_size
grid_height = screen_height // grid_size

# player
player_size = [40,40]
player_image = GameImage("new_tank_image.png", player_size).image
player_pos = pygame.math.Vector2(100, screen_height / 2)
direction = pygame.math.Vector2(1,1)
player_speed = 7.5
rotation_speed = 15
angle = 0
player_health = 5

# bot (bot1 = bot, bot2 = bot2)
bot_size = [40,40]
bot_image = GameImage("enemytank_image.png", bot_size).image
bot_pos = pygame.math.Vector2(screen_length -100 , 100)
bot2_pos = pygame.math.Vector2(screen_length -100, screen_height-100)
bot_speed = 3
bot_angle = 0
bot_rotation_speed = rotation_speed
bot_shooting_speed = 2000
bot_health = 5
bot1_start_pos = bot_pos.copy()
bot2_start_pos = bot2_pos.copy()

# bullet
bullet_size = [10,25]
bullet_speed = 20
bullet_list_player = []
bullet_list_bot = []
bullet_list_bot2 = []
bullet_image = GameImage("bullet_image1.png", bullet_size).image
bullet_cooldown = 2000
ammo_pos = [10,70]
max_ammo = 3

# special bullet
special_bullet_image = GameImage("bullet_special.png", bullet_size).image

# wall
list_of_objects = [] #walls en bushes worden in deze lijst geplaatst
wall_size = [35,35]
wall_image = GameImage("brick_wall.png", wall_size).image
wall_amount = 10

# bush
bush_size = [35,35]
bush_image = GameImage("bush.png", bush_size).image
bush_amount = 10

# heart
playerheart_size = [50,50]
botheart_size = [15,15]
playerheart_image = GameImage("heart.png", playerheart_size).image
botheart_image = GameImage("heart.png", botheart_size).image
heart_pos = [10,10]

# powerups 
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

# lock 
lock_image = GameImage("lock.png", [50,50]).image

# buttons
text_colour=(255,255,255)
background_colour=(100,100,100)
hover_colour=(200,200,200)


class Object:
    def __init__(self,pos):
        self.pos = pos
    
    def collision(self, otherObject):
    # Controleer of beide objecten een rect attribuut hebben
        if hasattr(self, 'rect') and hasattr(otherObject, 'rect'):
            return self.rect.colliderect(otherObject.rect) # geeft True bij botsing, False bij geen botsing
        return False  # als een van de objecten geen rect heeft, return False

class StationaryObject(Object):
    def __init__(self,pos):
        super().__init__(pos)
        self.grid_x = int(self.pos[0]) // grid_size
        self.grid_y = int(self.pos[1]) // grid_size

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
