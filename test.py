import pygame, os

# GLOBAL VARIABLES
COLOR = (255, 100, 98)
SURFACE_COLOR = (167, 255, 100)
WIDTH = 1000
HEIGHT = 1000

# Object class
class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
        super().__init__()

        img = pygame.image.load(os.getcwd()+"/vehicles/Porsche Cup 992/default.png")
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.blit(pygame.transform.scale(img, (width, height)), (0, 0))

        # pygame.draw.rect(self.image,(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),pygame.Rect(0, 0, width, height))

        self.rect = self.image.get_rect()


pygame.init()

RED = (255, 0, 0)

size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Creating Sprite")

all_sprites_list = pygame.sprite.Group()

object_ = Sprite(RED, 773/2, 773/2)
object_.rect.x = 200
object_.rect.y = 300

all_sprites_list.add(object_)

exit = True
clock = pygame.time.Clock()

while exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = False

    all_sprites_list.update()
    screen.fill(SURFACE_COLOR)
    object_.rect.x += 1
    all_sprites_list.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()