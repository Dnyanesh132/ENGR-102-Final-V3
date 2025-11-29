import pygame
from .scene_template import Scene
from .ui_button import Button

class instructions_screen(Scene):
    def __init__(self):
        super().__init__(None, "title_screen")
        
        # Background - using title background as placeholder
        try:
            self.background = pygame.image.load("assets/backgrounds/title_bg.png").convert()
        except:
            self.background = None
        
        self.bg_scaled = None
        
        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.section_font = pygame.font.Font(None, 50)
        self.text_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 28)
        
        # Scroll position
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 30
        
        # Instruction text organized by sections
        self.instruction_sections = self._build_instructions()
        
        # Back button
        self.back_btn = Button("BACK (ESC)", (100, 50), self.text_font, (255, 255, 255), (255, 200, 0))
        
        # UI dimensions
        self.content_width = 1000
        self.content_padding = 40
        self.line_height = 35
        self.section_spacing = 50
        
    def _build_instructions(self):
        """Build the instruction text structure"""
        sections = []
        
        # Title
        sections.append({
            "type": "title",
            "text": "SUGAR RUSH — GAME INSTRUCTIONS"
        })
        
        # Objective
        sections.append({
            "type": "section",
            "title": "Objective",
            "content": [
                "You and your twin brother are on a mission to earn enough money to buy a PS5…",
                "by becoming the greatest kindergarten candy dealers of all time.",
                "",
                "Play through each school period, win mini-games, avoid teachers and bullies,",
                "and manage your candy empire like a pro."
            ]
        })
        
        # Cursor & Menu Controls
        sections.append({
            "type": "section",
            "title": "Cursor & Menu Controls",
            "subsections": [
                {
                    "title": "Menu Navigation",
                    "content": [
                        "Mouse Cursor → Move through menu options",
                        "Left Click → Select",
                        "ESC → Go back / close windows"
                    ]
                },
                {
                    "title": "Start Menu Options",
                    "content": [
                        "Start New Game – Begin a new day",
                        "Load Game – Continue your progress",
                        "Instructions – View how to play",
                        "Quit Game – Exit to desktop"
                    ]
                }
            ]
        })
        
        # Game Loop Overview
        sections.append({
            "type": "section",
            "title": "Game Loop Overview",
            "content": [
                "Each school day is broken into time-based scenes:",
                "",
                "Class Time — 9 AM to 11 AM",
                "Lunch Break — 11 AM to 1 PM",
                "Hallway — 1 PM to 3 PM",
                "Brother Mark's Turn — 3 PM to 6 PM",
                "",
                "A full hour in the game = 60 real seconds.",
                "Watch the analog clock at the bottom right to manage your time wisely."
            ]
        })
        
        # Resources
        sections.append({
            "type": "section",
            "title": "Your Resources",
            "content": [
                "Displayed in the top-right corner:",
                "",
                "Buyers – How many kids are interested today",
                "Cash – Your money",
                "Candy – How much candy you're holding",
                "",
                "Candy Types:",
                "  Twizzles – Buy $1 / Sell $2",
                "  Skizzles – Buy $5 / Sell $9",
                "  Woozers – Buy $30 / Sell $40",
                "",
                "Costco gives bulk discounts later in the game."
            ]
        })
        
        # Class Time
        sections.append({
            "type": "section",
            "title": "1. Class Time (9–11 AM)",
            "subsections": [
                {
                    "title": "Goal:",
                    "content": ["Find classmates interested in buying candy later."]
                },
                {
                    "title": "Controls",
                    "content": [
                        "Arrow Keys/WASD → Move",
                        "E → Talk to students",
                        "Avoid the Teacher's Detection Circle (big red transparent bubble)"
                    ]
                },
                {
                    "title": "Mini-Game:",
                    "content": [
                        "Negotiate when talking to students. Successful talks increase",
                        "your buyers for lunch."
                    ]
                },
                {
                    "title": "If You're Caught",
                    "content": [
                        "Teacher sends you to the Naughty Corner",
                        "Lose time",
                        "Can't negotiate during that penalty"
                    ]
                }
            ]
        })
        
        # Lunch Break
        sections.append({
            "type": "section",
            "title": "2. Lunch Break (11 AM – 1 PM)",
            "subsections": [
                {
                    "title": "Goal:",
                    "content": ["Sell candy to your confirmed buyers."]
                },
                {
                    "title": "Controls",
                    "content": [
                        "Move close to a highlighted buyer",
                        "Press:",
                        "  1 → Sell Twizzles",
                        "  2 → Sell Skizzles",
                        "  3 → Sell Woozers",
                        "",
                        "+ / – → Change how many pieces you sell per deal"
                    ]
                },
                {
                    "title": "Threat: Bullies",
                    "content": [
                        "3 bullies wander around",
                        "If touched:",
                        "  Lose 10% of your cash",
                        "  Lose 30 seconds",
                        "  Bully freezes in place afterward (mercy mechanic)"
                    ]
                }
            ]
        })
        
        # Hallway
        sections.append({
            "type": "section",
            "title": "3. Hallway (1 PM – 3 PM)",
            "subsections": [
                {
                    "title": "Goal:",
                    "content": ["Reach the Principal's Son's contraband store."]
                },
                {
                    "title": "Controls",
                    "content": [
                        "Arrow keys/WASD → Move",
                        "E → Interact with Hall Monitor & Store"
                    ]
                },
                {
                    "title": "Hall Monitor",
                    "content": [
                        '"You gotta pay the candy toll, buddy."',
                        "",
                        "Must give him 1 candy of any type to pass."
                    ]
                },
                {
                    "title": "Contraband Store Items",
                    "content": [
                        "Bicycle – Helps your brother use less time traveling",
                        "Costco Membership – Bulk candy deals",
                        "Candy Machine – Generates 10 free candy/day",
                        "Bigger Backpack – Carry more items"
                    ]
                }
            ]
        })
        
        # Brother Mark's Turn
        sections.append({
            "type": "section",
            "title": "4. Brother Mark's Turn (3 PM – 6 PM)",
            "subsections": [
                {
                    "title": "Goal:",
                    "content": ["Travel home safely & buy supplies."]
                },
                {
                    "title": "🎮 Mini-Game: Rhythm Walking",
                    "content": [
                        "Press Left / Right alternating",
                        "",
                        "Must get:",
                        "  20 steps if walking",
                        "  10 steps if biking",
                        "",
                        "Mess up = Mark falls and must restart."
                    ]
                }
            ]
        })
        
        # Saving & Loading
        sections.append({
            "type": "section",
            "title": "Saving & Loading",
            "content": [
                "Your progress auto-saves when a scene ends.",
                "You can Load Game from the main menu at any time."
            ]
        })
        
        return sections
    
    def process_input(self, events):
        super().process_input(events)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for e in events:
            # ESC to go back
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.switch_to("title_screen")
            
            # Back button click
            if self.back_btn.clicked(mouse_pos, e):
                self.switch_to("title_screen")
        
        # Scroll with mouse wheel
        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                self.scroll_y -= e.y * self.scroll_speed
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
    
    def update(self, dt):
        super().update(dt)
        
        mouse_pos = pygame.mouse.get_pos()
        self.back_btn.update(mouse_pos)
        
        # Calculate max scroll based on content height
        # This will be recalculated in render with actual screen size
        self.scroll_y = max(0, self.scroll_y)
    
    def _calculate_content_height(self):
        """Calculate total height of all content"""
        height = 100  # Top padding
        for section in self.instruction_sections:
            if section["type"] == "title":
                height += 60
            elif section["type"] == "section":
                height += 50  # Section title
                if "content" in section:
                    height += len(section["content"]) * self.line_height
                if "subsections" in section:
                    for subsection in section["subsections"]:
                        height += 40  # Subsection title
                        height += len(subsection["content"]) * self.line_height
            height += self.section_spacing
        return height
    
    def render(self, screen):
        super().render(screen)
        
        # Scale background if needed
        if self.background:
            if self.bg_scaled is None:
                self.bg_scaled = pygame.transform.scale(self.background, screen.get_size())
            screen.blit(self.bg_scaled, (0, 0))
        else:
            # Pastel background color if no image
            screen.fill((255, 240, 245))  # Light pink pastel
        
        # Draw main content box with rounded corners effect
        screen_w, screen_h = screen.get_size()
        box_x = (screen_w - self.content_width) // 2
        box_y = 100
        box_h = screen_h - 200
        
        # Calculate max scroll based on actual content and viewport
        total_height = self._calculate_content_height()
        self.max_scroll = max(0, total_height - box_h + 40)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        
        # Draw shadow
        shadow_rect = pygame.Rect(box_x + 5, box_y + 5, self.content_width, box_h)
        pygame.draw.rect(screen, (200, 200, 200, 100), shadow_rect, border_radius=15)
        
        # Draw main box (pastel yellow/cream with rounded corners)
        main_rect = pygame.Rect(box_x, box_y, self.content_width, box_h)
        pygame.draw.rect(screen, (255, 250, 220), main_rect, border_radius=15)
        pygame.draw.rect(screen, (200, 180, 150), main_rect, width=3, border_radius=15)
        
        # Create a surface for scrollable content
        content_surface = pygame.Surface((self.content_width - 20, self._calculate_content_height()))
        content_surface.fill((255, 250, 220))  # Match background
        
        # Draw content on scrollable surface
        y_offset = 20 - self.scroll_y
        
        for section in self.instruction_sections:
            if section["type"] == "title":
                title_surf = self.title_font.render(section["text"], True, (139, 69, 19))  # Brown
                content_surface.blit(title_surf, (self.content_padding, y_offset))
                y_offset += 60
            
            elif section["type"] == "section":
                # Section title
                section_surf = self.section_font.render(section["title"], True, (255, 100, 150))  # Pink
                content_surface.blit(section_surf, (self.content_padding, y_offset))
                y_offset += 50
                
                # Section content
                if "content" in section:
                    for line in section["content"]:
                        if line:  # Skip empty lines
                            text_surf = self.text_font.render(line, True, (50, 50, 50))  # Dark gray
                            content_surface.blit(text_surf, (self.content_padding + 20, y_offset))
                        y_offset += self.line_height
                
                # Subsections
                if "subsections" in section:
                    for subsection in section["subsections"]:
                        # Subsection title
                        sub_title_surf = self.small_font.render(subsection["title"], True, (100, 150, 255))  # Light blue
                        content_surface.blit(sub_title_surf, (self.content_padding + 20, y_offset))
                        y_offset += 40
                        
                        # Subsection content
                        for line in subsection["content"]:
                            if line:  # Skip empty lines
                                text_surf = self.text_font.render(line, True, (50, 50, 50))
                                content_surface.blit(text_surf, (self.content_padding + 40, y_offset))
                            y_offset += self.line_height
                
                y_offset += self.section_spacing
        
        # Clip and blit scrollable content with scroll offset
        viewport_rect = pygame.Rect(0, self.scroll_y, self.content_width - 20, box_h - 40)
        screen.blit(content_surface, (box_x + 10, box_y + 20), viewport_rect)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            scroll_bar_height = box_h - 40
            scroll_bar_y = box_y + 20
            scroll_thumb_height = max(20, int(scroll_bar_height * (scroll_bar_height / (self._calculate_content_height() + 20))))
            scroll_thumb_y = scroll_bar_y + int((self.scroll_y / self.max_scroll) * (scroll_bar_height - scroll_thumb_height))
            
            # Scroll bar background
            bar_rect = pygame.Rect(box_x + self.content_width - 25, scroll_bar_y, 10, scroll_bar_height)
            pygame.draw.rect(screen, (220, 220, 220), bar_rect, border_radius=5)
            
            # Scroll thumb
            thumb_rect = pygame.Rect(box_x + self.content_width - 25, scroll_thumb_y, 10, scroll_thumb_height)
            pygame.draw.rect(screen, (150, 150, 150), thumb_rect, border_radius=5)
        
        # Draw back button
        self.back_btn.draw(screen)
        
        # Draw scroll hint at bottom
        if self.max_scroll > 0:
            hint_text = "Scroll with mouse wheel"
            hint_surf = self.small_font.render(hint_text, True, (100, 100, 100))
            hint_rect = hint_surf.get_rect(center=(screen_w // 2, screen_h - 30))
            screen.blit(hint_surf, hint_rect)

