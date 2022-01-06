import pygame
from sys import exit
from Level import Level
from actors import  PlayerActor, Wraith1, Wraith2, Wraith3
from menu import Menu
from settings import *
from gamedata import level_1_map, level_2_map, level_3_map

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
menu = Menu(screen)





lvl = 1
completed = False
# Menu Loop
while True:
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    if not completed:
        is_started, is_continued = menu.run(events)
        pygame.display.update()


    # Reset Level and Next Level
    if is_started and not is_continued and not completed:
        current_level = Level(screen, "assets/background", level_1_map)


    if completed:
        if lvl == 1:
            current_level = Level(screen, "assets/background", level_1_map)
            is_started = True
        elif lvl == 2:
            current_level = Level(screen, "assets/background", level_2_map)
            is_started = True
        elif lvl == 3:
            current_level = Level(screen, "assets/background", level_3_map)
            is_started = True
        elif lvl == 4:
            lvl = 1
            is_started = False
            completed = False


    
    # Game Loop
    while is_started:
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_started = False
                    menu.paused = True

                if event.key == pygame.K_KP5:
                    if lvl == 1:
                        current_level = Level(screen, "assets/background", level_2_map)
                        lvl = 2
                    elif lvl == 2:
                        current_level = Level(screen, "assets/background", level_3_map)
                        lvl = 3
                    else:
                        current_level = Level(screen, "assets/background", level_1_map)
                        lvl = 1

        

        completed = current_level.run(events, keys)

        # if player dies
        if current_level.player.health == 0:
            is_started = False
            menu.paused = False
            lvl = 1
        
        # If level completed
        if completed:
            lvl += 1
            break

        pygame.display.update()
        clock.tick(FPS)
