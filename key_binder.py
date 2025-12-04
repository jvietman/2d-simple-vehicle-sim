import pygame

pygame.display.set_mode((600, 600))

while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT: exit()

    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        print("Key: "+str(event.__dict__["key"])+"   State: "+str(event.type == pygame.KEYDOWN))
    
    pygame.display.update()