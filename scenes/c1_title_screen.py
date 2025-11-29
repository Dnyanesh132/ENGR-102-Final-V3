import pygame
from .scene_template import Scene
from .ui_button import Button
#importing button class we made ^^^


'''
class title_screen(Scene):
    def __init__(self):
        super().__init__(None, "intro")

    def process_input(self, events):
        super().process_input(events)
        
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.switch_to("intro")

    def render(self, screen):
        super().render(screen)
        text = self.font.render("Press any key to start. Press ESC to exit game at any time.", True, (255,255,255))
        screen.blit(text, (100,100))
'''


#used generative ai for this.

class title_screen(Scene):
    def __init__(self):
        super().__init__(None, "intro")

        # Background image (replace file path with your own)
        self.background = pygame.image.load("assets/backgrounds/title_bg.png").convert()
        
        # Scale background to screen size later in render()
        self.bg_scaled = None

        # Fonts
        self.title_font = pygame.font.Font(None, 120)
        self.button_font = pygame.font.Font(None, 60)

        # Buttons (positions are centered)
        self.buttons = []
        self.make_buttons()

        # Instruction popup
        self.show_instructions = True
        self.instruction_text = [
            "Welcome to SUGAR RUSH!",
            "",
            "Goal:",
            "  - Run your candy empire",
            "  - Upgrade machines",
            "  - Manage customers",
            "  - Make $$$",
            "",
            "Press SPACE to continue"
        ]

    def make_buttons(self):
        screen_w, screen_h = 900, 600
        cx = screen_w // 2

        self.play_btn = Button("PLAY", (cx, 280), self.button_font, (255,255,255), (255,200,0))
        self.load_btn = Button("LOAD SAVE", (cx, 360), self.button_font, (255,255,255), (255,200,0))
        self.instructions_btn = Button("INSTRUCTIONS", (cx, 440), self.button_font, (255,255,255), (255,200,0))
        self.quit_btn = Button("QUIT", (cx, 520), self.button_font, (255,255,255), (255,100,100))

        self.buttons = [self.play_btn, self.load_btn, self.instructions_btn, self.quit_btn]

    def process_input(self, events):
        super().process_input(events)

        mouse_pos = pygame.mouse.get_pos()

        for e in events:
            # Close instructions popup
            if self.show_instructions:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    self.show_instructions = False
                return  # do NOT process buttons until popup is closed

            # Handle quitting
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

            # Button clicks
            for btn in self.buttons:
                if btn.clicked(mouse_pos, e):
                    if btn == self.play_btn:
                        # Reset save to default values for new game
                        from save_manager import DEFAULT_DATA, save_data
                        save_data(DEFAULT_DATA.copy())
                        self.switch_to("intro")
                    elif btn == self.load_btn:
                        self.switch_to("load_save")  # you'll create this scene
                    elif btn == self.instructions_btn:
                        self.switch_to("instructions")
                    elif btn == self.quit_btn:
                        pygame.quit()
                        quit()

    def update(self, dt):
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()

        if not self.show_instructions:
            for btn in self.buttons:
                btn.update(mouse_pos)

    def render(self, screen):
        super().render(screen)

        # Scale background if not done yet
        if self.bg_scaled is None:
            self.bg_scaled = pygame.transform.scale(self.background, screen.get_size())

        # Draw background
        screen.blit(self.bg_scaled, (0, 0))

        # Title text
        title_surf = self.title_font.render("SUGAR RUSH", True, (255, 215, 0))
        rect = title_surf.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_surf, rect)

        # Draw buttons if not in instructions
        if not self.show_instructions:
            for btn in self.buttons:
                btn.draw(screen)

        # Instructions popup
        if self.show_instructions:
            self.draw_instruction_popup(screen)

    def draw_instruction_popup(self, screen):
        w, h = screen.get_size()

        # Dim background
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Popup box
        box_w, box_h = 600, 400
        box_rect = pygame.Rect((w-box_w)//2, (h-box_h)//2, box_w, box_h)

        pygame.draw.rect(screen, (50, 50, 50), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 4)

        # Draw text lines
        y = box_rect.y + 40
        for line in self.instruction_text:
            surf = self.font.render(line, True, (255, 255, 255))
            screen.blit(surf, (box_rect.x + 40, y))
            y += 40


#test again
#this is another test
#this is a test to see if github works for dnyanesh
#github test for ateeb