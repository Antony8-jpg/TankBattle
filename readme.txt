Prompts van chatgpt:

Question: Why does the bot always go for the shield even though there is a 50% chance?
Answer:
Yes — you're right to feel that the bots always seem to go for the shield. Here's what's really happening:

🔍 Current Logic Breakdown:
This line is the key:

python
Copy
Edit
if shield_spawner.powerup and self.state != "shield":
    if random.randint(1, 2) == 1:
random.randint(1, 2) == 1 gives a 50% chance every single frame the bot is not already in "shield" state and a shield exists. But because your bot logic is inside the game loop, and runs every frame, this condition gets checked continuously, meaning eventually (within a few frames), it's nearly guaranteed to pass for all bots — especially since bots check it independently.

Question: soms blijft de bot stil voor een seconde (geen echt probleem) en als hij dan schiet blijft de kogel staan ,hoe kan ik dit oplossen?
Answer:
The issue where the bot sometimes shoots a bullet that stays still (especially when it's not moving) is likely because the direction vector used in the Bot.shoot() method is zero or nearly zero at the time of shooting:

python
Copy
Edit
bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
If self.direction is (0, 0), then bullet.launch() will not update its position, so the bullet appears stuck.

✅ Fix
Ensure that the bot always shoots in the direction it's facing, even if self.direction is zero:

Update Bot.shoot():
def shoot(self):
    current_time = pygame.time.get_ticks()
    if current_time - self.last_shot_time > bot_shooting_speed:
        self.last_shot_time = current_time

        # Calculate direction from angle if current direction is zero
        if self.direction.length_squared() == 0:
            rad_angle = math.radians(-self.angle - 90)
            self.direction = pygame.math.Vector2(math.cos(rad_angle), math.sin(rad_angle))

        bullet = Bullet(self.pos.copy(), self.direction.copy(), bullet_speed, self.angle, bullet_image)
        bullet_list_bot.append(bullet)
# we hebben deze code verandert en dan toegepast

Question: how can i add a function that draws a circle, but still keep the button class as it is?
Answer:
Perfect — you want to keep the Button class as-is but add an optional way to draw it as a circle, used only when needed.

Here's how to do that without breaking existing rectangular buttons:

✅ Step 1: Modify the Button class to optionally support circle drawing
Add an optional is_circle flag and radius:

class Button:
    def __init__(self, rect, text, font, text_colour, background_colour, hover_colour, is_circle=False, radius=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.hover_colour = hover_colour
        self.is_circle = is_circle
        self.radius = radius
        if is_circle and radius is None:
            self.radius = min(self.rect.width, self.rect.height) // 2  # fallback radius
✅ Step 2: Modify draw() to handle both rectangle and circle
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        if self.is_circle:
            center = self.rect.center
            dist = math.hypot(mouse_pos[0] - center[0], mouse_pos[1] - center[1])
            is_hovered = dist <= self.radius
        else:
            is_hovered = self.rect.collidepoint(mouse_pos)

        current_colour = self.hover_colour if is_hovered else self.background_colour

        if self.is_circle:
            pygame.draw.circle(surface, current_colour, self.rect.center, self.radius)
        else:
            pygame.draw.rect(surface, current_colour, self.rect)

        text_surf = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

Question:
