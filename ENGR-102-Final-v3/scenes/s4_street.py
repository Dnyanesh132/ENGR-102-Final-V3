import pygame
from .scene_template import Scene

class street(Scene):
    def __init__(self):
        # Initialize the scene to follow and the duration of the current scene
        super().__init__(90, "store")
        if self.save["has_costco_membership"]:
            self.default_next_scene = "costco"
        
        # Initial player position (x, y)
        self.player_pos = pygame.math.Vector2(100, 100)
        
    def process_input(self, events):
        super().process_input(events)
        
    def update(self, dt):
        super().update(dt)
        
    def render(self, screen):
        return super().render(screen)