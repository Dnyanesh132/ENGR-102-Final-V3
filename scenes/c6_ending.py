import pygame
from .scene_template import Scene

class ending(Scene):
    def __init__(self):
        super().__init__(None, "title_screen")  # No auto-transition, player can read credits
        self.scroll_offset = 0
        self.scroll_speed = 30  # Pixels per second

    def process_input(self, events):
        super().process_input(events)
        
        # Allow player to skip credits with any key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.switch_to("title_screen")

    def update(self, dt):
        super().update(dt)
        
        # Auto-scroll credits
        self.scroll_offset += self.scroll_speed * dt
        
        # If scrolled past end, allow transition
        if self.scroll_offset > 2000:  # Adjust based on content length
            pass  # Credits finished scrolling

    def render(self, screen):
        super().render(screen, tool_tips=False)
        
        # Dark background
        screen.fill((0, 0, 0))
        
        # Credits text (you can customize this)
        credits = [
            "GAME COMPLETED!",
            "",
            "You successfully bought the PS5!",
            "",
            "CREDITS",
            "",
            "Aires",
            "Ateeb",
            "Dnyanesh",
            "Yashas",
            "",
            "Special Thanks:",
            "Professor Spears",
            "",
            "",
            "Press ESC or SPACE to return to title screen",
        ]
        
        # Draw credits with scrolling
        y_start = screen.get_height() - int(self.scroll_offset)
        title_font = pygame.font.Font(None, 60)
        large_font = pygame.font.Font(None, 48)
        
        for i, credit_line in enumerate(credits):
            y_pos = y_start + (i * 50)
            
            # Skip if off screen
            if y_pos < -50 or y_pos > screen.get_height() + 50:
                continue
            
            # Choose font based on line
            if i == 0:  # if game is completed
                font = title_font
                color = (255, 255, 0)
            elif i == 4:  #credit scence
                font = large_font
                color = (255, 215, 0)
            else:
                font = self.font
                color = (255, 255, 255)
            
            text_surface = font.render(credit_line, True, color)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, y_pos))
            screen.blit(text_surface, text_rect)
        
        # Draw instruction at bottom
        if self.scroll_offset > 1500:
            inst_text = "Press ESC or SPACE to return to title screen"
            inst_surface = self.font.render(inst_text, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))
            screen.blit(inst_surface, inst_rect)
