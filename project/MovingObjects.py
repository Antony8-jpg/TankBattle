import pygame

#import files
from Variabels import *
from ScreenObjects import *
from StationaryObjects import *

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
