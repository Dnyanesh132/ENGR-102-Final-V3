import pygame
from save_manager import load_save, save_data

from scenes.c1_title_screen import title_screen
from scenes.c2_instructions import instructions_screen
from scenes.c3_load_save_menu import load_save_menu
from scenes.c4_brother_a_transition import brother_a_transition
from scenes.c5_brother_b_transition import brother_b_transition
from scenes.c6_ending import ending
from scenes.s1_classroom import classroom
from scenes.s2_playground import playground
from scenes.s3_hallway import hallway
from scenes.s4_street import street
from scenes.s5a_store import store
from scenes.s5b_costco import costco

SCENES = {
    "title_screen":title_screen,
    "inst..uctions":instructions_screen,
    "load_save": load_save_menu,
    "brother_a_transition":brother_a_transition,
    "brother_b_transition":brother_b_transition,
    "ending":ending,
    "classroom":classroom,
    "playground":playground,
    "hallway":hallway,
    "street":street,
    "store":store,
    "costco":costco
}

save = load_save()

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

current_scene = SCENES["title_screen"]()

running = True
while running:
    ########## initialize the time and create the variable for it #########
    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    ######## check for the event "quit" and exit out if needed #########
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    current_scene.process_input(events)
    current_scene.update(dt)
    current_scene.render(screen)

    if current_scene.next_scene != current_scene:
        current_scene = SCENES[current_scene.next_scene]()

    pygame.display.flip()

pygame.quit()