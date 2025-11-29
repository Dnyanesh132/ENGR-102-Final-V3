import pygame
from .scene_template import Scene

class ending(Scene):
    def __init__(self):
        super().__init__(10, "title_screen")

    def process_input(self, events):
        super().process_input(events)

    def render(self, screen):
        super().render(screen)
        
        text = self.font.render("Game Completed!", True, (255,255,255))
        screen.blit(text, (100,100))
