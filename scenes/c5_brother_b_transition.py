import pygame
from .scene_template import Scene

class brother_b_transition(Scene):
    def __init__(self):
        # Show transition for 3 seconds, then go to street
        super().__init__(3.0, "street")
        self.large_font = pygame.font.Font(None, 72)
        
    def process_input(self, events):
        super().process_input(events)
        
        # Allow skipping with any key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.switch_to("street")
    
    def render(self, screen):
        super().render(screen)
        
        # Dark background
        screen.fill((0, 0, 0))
        
        # Transition message
        message_text = "You are now playing as Brother Mark"
        message_surface = self.large_font.render(message_text, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(message_surface, message_rect)
        
        # Skip hint
        skip_text = "Press SPACE to continue"
        skip_surface = self.font.render(skip_text, True, (200, 200, 200))
        skip_rect = skip_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 80))
        screen.blit(skip_surface, skip_rect)
