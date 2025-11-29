import pygame
from .scene_template import Scene

class intro(Scene):
    def __init__(self):
        super().__init__(2, "classroom")

    def process_input(self, events):
        super().process_input(events)

    def render(self, screen):
        super().render(screen)
        
        text = self.font.render("You are now playing as Brother A", True, (255,255,255))
        screen.blit(text, (100,100))
