import pygame
from .scene_template import Scene

class street(Scene):
    def __init__(self):
        # Initial player position (x, y)
        initial_pos = pygame.math.Vector2(100, 360)
        super().__init__(180, "store", "street.png", "Andrew", initial_pos)

        # Check if has costco membership to determine next scene
        if self.save["has_costco_membership"]:
            self.default_next_scene = "costco"

        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 48)

        # Collision boxes
        self.collision_boxes = [
            pygame.Rect(-1, 0, 1, 720),  # Left wall
            pygame.Rect(0, -1, 1280, 1),  # Top wall
            pygame.Rect(1280, 0, 1, 720),  # Right wall
            pygame.Rect(0, 720, 1280, 1),  # Bottom wall
        ]
        
        # Load Andrew's sprite
        andrew_original = pygame.image.load("assets/mark.png").convert_alpha()
        andrew_width, andrew_height = andrew_original.get_size()
        andrew_scale = 60 / andrew_height
        self.andrew_sprite = pygame.transform.scale(andrew_original, (int(andrew_width * andrew_scale), 60))
        
        # Rhythm walking mini-game state
        self.in_rhythm_game = True  # Start in rhythm game
        self.rhythm_steps_completed = 0
        self.rhythm_target_steps = 20  # Default: 20 steps if walking
        self.rhythm_last_key = None  # Track last key pressed (LEFT or RIGHT)
        self.rhythm_waiting_for_key = True  # Waiting for first key press
        self.rhythm_failed = False
        self.rhythm_fail_timer = 0.0
        self.rhythm_fail_duration = 1.5  # Show failure message for 1.5 seconds
        
        # Random countdown timing system
        import random
        self.rhythm_countdown_active = True  # Start with first countdown
        self.rhythm_countdown_timer = 0.0
        self.rhythm_countdown_duration = random.uniform(0.5, 1.5)  # Random between 0.5-1.5 seconds
        self.rhythm_can_press = False  # Can only press during the window
        self.rhythm_press_window = 0.3  # 0.3 second window to press
        self.rhythm_press_window_timer = 0.0
        
        # Track if rhythm game was completed successfully
        self.rhythm_game_completed = False
        
        # Check if has bicycle (affects target steps)
        if self.save.get("has_bicycle", False):
            self.rhythm_target_steps = 10  # 10 steps if biking
        
    def process_input(self, events):
        super().process_input(events)
        
        # Disable normal movement during rhythm game
        if self.in_rhythm_game:
            self.movement = pygame.math.Vector2(0, 0)
        
        # Handle rhythm game input
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Skip time is handled in base Scene class
                if self.in_rhythm_game and not self.rhythm_failed:
                    if event.key == pygame.K_LEFT:
                        self.handle_rhythm_key("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.handle_rhythm_key("RIGHT")
    
    def update(self, dt):
        # Update timer manually (don't call super().update() to prevent auto-transition)
        if self.duration is not None:
            self.timer += dt
            
            # Check if timer expired - if rhythm game wasn't completed, go to Brother A's turn
            if self.timer >= self.duration:
                if not self.rhythm_game_completed:
                    # Failed to complete rhythm game in time - go straight to Brother A
                    self.switch_to("brother_a_transition")
                    return
                # If completed, the transition already happened in handle_rhythm_key
                return
        
        # Update rhythm game failure timer
        if self.rhythm_failed:
            self.rhythm_fail_timer += dt
            if self.rhythm_fail_timer >= self.rhythm_fail_duration:
                self.rhythm_failed = False
                self.rhythm_fail_timer = 0.0
                # Restart countdown after failure
                if self.in_rhythm_game:
                    self.start_next_countdown()
        
        # Update rhythm countdown timing
        if self.in_rhythm_game and not self.rhythm_failed and self.rhythm_countdown_active:
            self.rhythm_countdown_timer += dt
            
            if self.rhythm_countdown_timer >= self.rhythm_countdown_duration:
                # Countdown finished - open press window
                self.rhythm_can_press = True
                self.rhythm_press_window_timer = 0.0
            elif self.rhythm_can_press:
                # In press window - check if window expired
                self.rhythm_press_window_timer += dt
                if self.rhythm_press_window_timer >= self.rhythm_press_window:
                    # Window expired - fail!
                    self.rhythm_failed = True
                    self.rhythm_fail_timer = 0.0
                    self.rhythm_steps_completed = 0
                    self.rhythm_last_key = None
                    self.rhythm_waiting_for_key = True
                    self.rhythm_countdown_active = False
                    self.rhythm_can_press = False
                    self.timer += 30
    
    def handle_rhythm_key(self, key_name):
        """Handle rhythm game key press - must alternate LEFT/RIGHT and be timed correctly"""
        # Can only press during the press window
        if not self.rhythm_can_press:
            # Pressed too early or too late = fail
            self.rhythm_failed = True
            self.rhythm_fail_timer = 0.0
            self.rhythm_steps_completed = 0
            self.rhythm_last_key = None
            self.rhythm_waiting_for_key = True
            self.rhythm_countdown_active = False
            self.rhythm_can_press = False
            self.timer += 30
            return
        
        # Check if alternating correctly
        if self.rhythm_waiting_for_key:
            # Record first key press
            self.rhythm_last_key = key_name
            self.rhythm_waiting_for_key = False
            self.rhythm_steps_completed += 1
            # Start next countdown
            self.start_next_countdown()
        else:
            # Must alternate
            if key_name != self.rhythm_last_key:
                # Corretly pressed alternate key
                self.rhythm_last_key = key_name
                self.rhythm_steps_completed += 1
                self.rhythm_can_press = False  # Reset press window
                
                # Check if completed
                if self.rhythm_steps_completed >= self.rhythm_target_steps:
                    # Exit rhythm game
                    self.in_rhythm_game = False
                    self.rhythm_game_completed = True
                    # Save remaining time and transition to store/costco
                    remaining_time = max(0, self.duration - self.timer)
                    self.save["brother_b_remaining_time"] = remaining_time
                    self.save_game()
                    self.switch_to(self.default_next_scene)
                else:
                    # Start next countdown
                    self.start_next_countdown()
            else:
                # Failed, pressed same rhythm key in a row
                self.rhythm_failed = True
                self.rhythm_fail_timer = 0.0
                self.rhythm_steps_completed = 0
                self.rhythm_last_key = None
                self.rhythm_waiting_for_key = True
                self.rhythm_countdown_active = False
                self.rhythm_can_press = False
                self.timer += 30
    
    def start_next_countdown(self):
        """Start a new random countdown before next key press"""
        import random
        self.rhythm_countdown_active = True
        self.rhythm_countdown_timer = 0.0
        self.rhythm_countdown_duration = random.uniform(0.5, 1.5)  # Random between 0.5-1.5 seconds
        self.rhythm_can_press = False
        self.rhythm_press_window_timer = 0.0

    def render(self, screen):
        super().render(screen, "Road")

        self.draw_rhythm_game_UI(screen)
        self.draw_clock(screen)
        self.draw_inventory(screen)

    def draw_rhythm_game_UI(self, screen):
        if self.in_rhythm_game:
            self.dim_background(screen)
            
            # Dimesions of the game box
            boxw, boxh = 600, 400
            boxx = (screen.get_width() - boxw) // 2
            boxy = (screen.get_height() - boxh) // 2

            self.draw_game_box(screen, boxx, boxy, boxw, boxh)
            self.draw_game_title(screen, boxx, boxy, boxw, boxh)
            self.draw_game_instructions(screen, boxx, boxy, boxw, boxh)
            self.draw_game_progress(screen, boxx, boxy, boxw, boxh)
            self.draw_game_countdown(screen, boxx, boxy, boxw, boxh)
            self.draw_game_fail(screen, boxx, boxy, boxw, boxh)
        else:
            # Rhythm game completed
            self.draw_andrew_moving(screen)            
            self.draw_completion_message(screen)
        
    def dim_background(self, screen):
        # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

    def draw_game_box(self, screen, box_x, box_y, box_w, box_h):
        # Rhythm game box
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (30, 30, 30), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 4)

    def draw_game_title(self, screen, box_x, box_y, box_w, box_h):
        # Title
            title_text = "RHYTHM WALKING"
            if self.save.get("has_bicycle", False):
                title_text = "RHYTHM BIKING"
            title_surface = self.large_font.render(title_text, True, (255, 255, 0))
            title_rect = title_surface.get_rect(center=(box_x + box_w // 2, box_y + 50))
            screen.blit(title_surface, title_rect)
    
    def draw_game_instructions(self, screen, box_x, box_y, box_w, box_h):
        # Instructions
            inst_text = "Alternate LEFT and RIGHT arrow keys"
            inst_surface = self.font.render(inst_text, True, (255, 255, 255))
            inst_rect = inst_surface.get_rect(center=(box_x + box_w // 2, box_y + 120))
            screen.blit(inst_surface, inst_rect)

    def draw_game_progress(self, screen, box_x, box_y, box_w, box_h):
        # Progress
            progress_text = f"Steps: {self.rhythm_steps_completed} / {self.rhythm_target_steps}"
            progress_surface = self.large_font.render(progress_text, True, (0, 255, 0))
            progress_rect = progress_surface.get_rect(center=(box_x + box_w // 2, box_y + 200))
            screen.blit(progress_surface, progress_rect)

    def draw_game_countdown(self, screen, box_x, box_y, box_w, box_h):
        # Countdown and timing hint
            if self.rhythm_countdown_active and not self.rhythm_can_press:
                # Show countdown
                countdown_text = f"Wait... {self.rhythm_countdown_duration - self.rhythm_countdown_timer:.1f}s"
                countdown_surface = self.font.render(countdown_text, True, (200, 200, 200))
                countdown_rect = countdown_surface.get_rect(center=(box_x + box_w // 2, box_y + 260))
                screen.blit(countdown_surface, countdown_rect)
            elif self.rhythm_can_press:
                # Show press window
                if not self.rhythm_waiting_for_key:
                    next_key = "RIGHT" if self.rhythm_last_key == "LEFT" else "LEFT"
                    hint_text = f"NOW! Press {next_key} arrow key!"
                else:
                    hint_text = "NOW! Press LEFT or RIGHT!"
                hint_surface = self.large_font.render(hint_text, True, (0, 255, 0))
                hint_rect = hint_surface.get_rect(center=(box_x + box_w // 2, box_y + 260))
                screen.blit(hint_surface, hint_rect)
                
                # Show window timer
                window_left = self.rhythm_press_window - self.rhythm_press_window_timer
                window_text = f"Window: {window_left:.2f}s"
                window_surface = self.small_font.render(window_text, True, (255, 255, 0))
                window_rect = window_surface.get_rect(center=(box_x + box_w // 2, box_y + 300))
                screen.blit(window_surface, window_rect)
            else:
                start_text = "Wait for the signal..."
                start_surface = self.font.render(start_text, True, (200, 200, 255))
                start_rect = start_surface.get_rect(center=(box_x + box_w // 2, box_y + 260))
                screen.blit(start_surface, start_rect)

    def draw_game_fail(self, screen, box_x, box_y, box_w, box_h):
         # Failure message
            if self.rhythm_failed:
                fail_text = "FAILED! Mark fell down. Restarting..."
                fail_surface = self.large_font.render(fail_text, True, (255, 0, 0))
                fail_rect = fail_surface.get_rect(center=(box_x + box_w // 2, box_y + 320))
                screen.blit(fail_surface, fail_rect)
                
                penalty_text = "-30 seconds penalty"
                penalty_surface = self.small_font.render(penalty_text, True, (255, 100, 100))
                penalty_rect = penalty_surface.get_rect(center=(box_x + box_w // 2, box_y + 360))
                screen.blit(penalty_surface, penalty_rect)

    def draw_andrew_moving(self, screen):
         # Draw Andrew moving across screen
            andrew_rect = self.andrew_sprite.get_rect(center=self.player_pos)
            screen.blit(self.andrew_sprite, andrew_rect)

    def draw_completion_message(self, screen):
         # Show completion message briefly
            if self.timer < 2.0:  # Show for first 2 seconds after completion
                complete_text = "Walking to store..."
                complete_surface = self.font.render(complete_text, True, (0, 255, 0))
                complete_rect = complete_surface.get_rect(center=(screen.get_width() // 2, 100))
                screen.blit(complete_surface, complete_rect)
