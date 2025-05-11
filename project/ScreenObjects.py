# import pygame

# import files
from Variabels import *

class Screen():
    def __init__(self,pos):
        self.pos = pos
    
    def draw_reload_timer(player):
        current_time = pygame.time.get_ticks()
        if player.ammo < max_ammo: # enkel als hij nog ammo moet bijkrijgen
            time_since_reload = current_time - player.last_reload_time
            progress = min(time_since_reload / bullet_cooldown, 1.0) # min(..,1.0) zorgt ervoor dat de progress niet groter dan 1 is
            bar_width = 50
            pygame.draw.rect(screen, (255, 0, 0), (ammo_pos[0], ammo_pos[1] + 40, bar_width, 10)) # lege bar tekenen in rood
            pygame.draw.rect(screen, (0, 255, 0), (ammo_pos[0], ammo_pos[1] + 40, progress * bar_width, 10)) # progress in bar tekenen in geel
            
    def available_positions():
        # geeft posities waar walles en bushes generate kunnen worden, overal maar niet aan de zijkanten, wall_size[] zijn de stappen
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
            
    def draw_shield_indicator(player, bot1,bot2):
        # shield player wordt naast health getoond
        # shield van de bot wordt naast de hartjes van de bot getoond
        list = [bot1,bot2]
        for object in list:
            if object.has_shield:
                spacing = bot_size[0] / max(object.health, 1)
                bot_heart_x = object.pos.x - bot_size[0]/2 + object.health * spacing
                bot_heart_y = object.pos.y - bot_size[1]
                screen.blit(botshield_image, (bot_heart_x + 5, bot_heart_y))
        if player.has_shield:
            x = heart_pos[0] + player.health * playerheart_size[0] + 5  # rechts van het laatste hartje
            y = heart_pos[1] 
            screen.blit(playershield_image, (x, y))

    def draw_speed_boost(player, position = (5, 165)):
        if player.speed_boost_active:
            screen.blit(speed_boost_image, position)
            current_time = pygame.time.get_ticks()
            time_since_start_boost = current_time - player.speed_boost_start_time
            duration = speed_boost_duration
            progress = max(0, min(1.0, 1 - time_since_start_boost / duration))  # balk gaat van 1 tot 0, max en min is zodat het altijd tussen 0 en 1 zit
            bar_width = 50
            bar_height = 10
            pygame.draw.rect(screen, (50, 50, 50), (5, 210, bar_width, bar_height)) #lege bar
            pygame.draw.rect(screen, (0, 150, 255), (5, 210, progress * bar_width, bar_height)) #progress bar

    def draw_end_screen(message):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (screen_length // 2 - text.get_width() // 2, screen_height // 4))
        instructions_button.draw(screen)
        
    def draw_unlocked(message):
        text = small_font.render(message, True, (255,255,255))
        screen.blit(text, (screen_length // 2 - text.get_width() //2, screen_height // 2))
        
    def draw_start_screen():
        screen.blit(main_background, (0,0))
        title = font.render("Tank Battle", True, (255, 255, 255))
        subtitle = small_font.render("Press ENTER to Start or i for instructions or use the buttons", True, (255, 255, 255))
        screen.blit(title, (screen_length // 2 - title.get_width() // 2, screen_height // 3))
        screen.blit(subtitle, (screen_length // 2 - subtitle.get_width() // 2, screen_height // 2))
        start_button.draw(screen)
        instructions_button.draw(screen)

    def draw_instruction_screen():
        screen.fill((0, 0, 0))
        instructions = [
            "Move with arrow keys",
            "Shoot bullets with SPACEBAR",
            "Shoot special bullet with F key",
            "Hearts represent your health",
            "Defeat the red enemy bot(s)!"
        ]
        title = font.render("Instructions", True, (255, 255, 255))
        screen.blit(title, (screen_length // 2 - title.get_width() // 2, 50))
        back_to_homescreen_button.draw(screen)
        start_button.draw(screen)

        for i, line in enumerate(instructions): # positie van de tekst en de lijn bijhouden
            line_render = small_font.render(line, True, (255, 255, 255))
            screen.blit(line_render, (screen_length // 2 - line_render.get_width() // 2, 150 + i * 60)) # positie van de tekst bepalen
        
    def draw_gamemode_screen():
        screen.fill((0,0,0))
        title = font.render("Choose a game mode", True, (255,255,255))
        screen.blit(title, (screen_length // 2 - title.get_width() // 2, 50))
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        

class Button():
    def __init__(self, rect, text, font, text_colour, background_colour, hover_colour,is_circle=False, radius=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.hover_colour = hover_colour
        self.circle = is_circle
        self.radius = radius
        if self.circle and radius is None:
            self.radius = min(self.rect.width, self.rect.height) // 2  # fallback radius

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        # kleur aanpassen
        if self.rect.collidepoint(mouse_pos):
            current_colour = self.hover_colour # lichtere kleur als de muis op die positie is 
        else:
            current_colour = self.background_colour
        # draw
        if self.circle: # circle
            pygame.draw.circle(surface, current_colour, self.rect.center, self.radius)
        else: # rectangle
            pygame.draw.rect(surface, current_colour, self.rect)

        text_surf = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left click
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

# letttertype 
font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 50)

# buttons
start_button = Button(rect=(screen_length//2 -100,520, 200, 60),
                      text="Start",
                      font=small_font,
                      text_colour = text_colour,
                      background_colour = background_colour,
                      hover_colour = hover_colour)
won_button = Button((screen_length //2 - 200 , 520, 400, 80),
                    "Play again!",
                    small_font,
                    text_colour,
                    background_colour,
                    hover_colour
                    )
lost_button = Button((screen_length //2 - 200 , 520, 400, 80),
                    "Get revenge!",
                    small_font,
                    text_colour,
                    background_colour,
                    hover_colour
                    )

instructions_button = Button((20,20, 40, 40),
                    "i",
                    small_font,
                    text_colour,
                    background_colour,
                    hover_colour,
                    is_circle = True
                    )
back_to_homescreen_button = Button((screen_length//2 -200,450, 400, 60),
                      "Back to main menu",
                      small_font,
                      text_colour,
                      background_colour,
                      hover_colour
                      )
easy_button = Button((screen_length//2 -100,250, 200, 60),
                      "Easy",
                      small_font,
                      text_colour,
                      background_colour,
                      hover_colour
                      )
medium_button = Button((screen_length//2 -100,350, 200, 60),
                      "Medium",
                      small_font,
                      text_colour,
                      background_colour,
                      hover_colour
                      )
hard_button = Button((screen_length//2 -100,450, 200, 60),
                      "Hard",
                      small_font,
                      text_colour,
                      background_colour,
                      hover_colour
                      )
