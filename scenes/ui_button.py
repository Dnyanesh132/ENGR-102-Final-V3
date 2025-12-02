import pygame

class Button:
    def __init__(self, text, pos, font, base_color, hover_color):
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color

        self.surface = self.font.render(text, True, base_color)
        self.rect = self.surface.get_rect(center=pos)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.surface = self.font.render(self.text, True, self.hover_color)
            return True
        else:
            self.surface = self.font.render(self.text, True, self.base_color)
            return False
        
    def clicked(self, mouse_pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos)