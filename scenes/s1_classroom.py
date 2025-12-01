import pygame
import random
from .scene_template import Scene

class classroom(Scene):
    def __init__(self):
        # Initial position
        initial_pos = pygame.math.Vector2(600, 400)
        super().__init__(120, "playground", "classroom.png", "Andrew", initial_pos)
        
        # Font for help text
        self.small_font = pygame.font.Font(None, 28)
        
        # Initialize collision boxes
        self.collision_boxes = [
            # Top wall
            pygame.Rect(0, 0, 1280, 196),
            # Bottom wall
            pygame.Rect(0, 577, 1280, 143),
            
            # Misc Objects:
            pygame.Rect(0, 196, 11, 20),
            pygame.Rect(13, 338, 113, 71),
            pygame.Rect(315, 338, 61, 71),
            
            # Small Desks
            pygame.Rect(210, 160, 235, 58),
            pygame.Rect(712, 263, 44, 100),
            pygame.Rect(873, 263, 44, 100),
            pygame.Rect(712, 406, 44, 100),
            pygame.Rect(873, 406, 44, 100),
            # Large Desk
            pygame.Rect(1033, 275, 87, 217),
            
            # Game window boundaries are below
            pygame.Rect(-1, 0, 1, 720),
            pygame.Rect(0, -1, 1280, 1),
            pygame.Rect(1280, 0, 1, 720),
            pygame.Rect(0, 720, 1280, 1),
        ]
        
        # Reset buyers at the start of a new day
        self.save["buyers"] = 0
        self.save_game()
        
        
        # Load sprites with proper aspect ratio scaling
        # Get original sprite dimensions to maintain aspect ratio
        
        andrew_original = pygame.image.load("assets/andrew.png").convert_alpha()
        andrew_width, andrew_height = andrew_original.get_size()
        # Scale to 60 pixels tall, maintain aspect ratio
        andrew_scale = 60 / andrew_height
        self.andrew_sprite = pygame.transform.scale(andrew_original, (int(andrew_width * andrew_scale) / 60 * 110 , 110))
        
        teacher_original = pygame.image.load("assets/teacher.png").convert_alpha()
        teacher_width, teacher_height = teacher_original.get_size()
        # Scale to 70 pixels tall, maintain aspect ratio
        teacher_scale = 70 / teacher_height
        self.teacher_sprite = pygame.transform.scale(teacher_original, (int(teacher_width * teacher_scale) / 70 * 120, 120))
        
        guy_npc_original = pygame.image.load("assets/guy_npc.png").convert_alpha()
        guy_width, guy_height = guy_npc_original.get_size()
        # Scale to 45 pixels tall, maintain aspect ratio
        guy_scale = 45 / guy_height
        self.guy_npc_sprite = pygame.transform.scale(guy_npc_original, (int(guy_width * guy_scale) / 45 * 80, 80))
        
        girl_npc_original = pygame.image.load("assets/girl_npc.png").convert_alpha()
        girl_width, girl_height = girl_npc_original.get_size()
        # Scale to 45 pixels tall, maintain aspect ratio
        girl_scale = 45 / girl_height
        self.girl_npc_sprite = pygame.transform.scale(girl_npc_original, (int(girl_width * girl_scale)/45 * 80, 80))
        
        
        # NPC positions next to desks (not on them) and interaction radius
        self.npcs = [
            {"sprite": self.guy_npc_sprite, "pos": pygame.math.Vector2(280, 220), "talked": False},  # Next to desk at 210, 160
            {"sprite": self.girl_npc_sprite, "pos": pygame.math.Vector2(680, 290), "talked": False},  # Next to desk at 712, 263
            {"sprite": self.guy_npc_sprite, "pos": pygame.math.Vector2(840, 290), "talked": False},  # Next to desk at 873, 263
            {"sprite": self.girl_npc_sprite, "pos": pygame.math.Vector2(680, 440), "talked": False},  # Next to desk at 712, 406
            {"sprite": self.guy_npc_sprite, "pos": pygame.math.Vector2(840, 440), "talked": False},  # Next to desk at 873, 406
            {"sprite": self.girl_npc_sprite, "pos": pygame.math.Vector2(70, 373), "talked": False},  # Kid in corner on carpet (around 13, 338)
        ]
        self.interaction_radius = 50  # Distance to interact with NPCs
        
        
        # Teacher position (at main desk, next to it - further from desk)
        # Large desk is at 1033, 275 with size 87x217
        # Position teacher to the right side, not on the desk
        self.teacher_pos = pygame.math.Vector2(1150, 380)  # Further right, next to large desk
        
        # Teacher's vision circle - smaller and zig-zag pattern
        self.vision_radius = 100  # Smaller radius
        self.vision_x = 300  # Starting position
        self.vision_y = 300  # Starting Y position
        self.vision_speed_x = 70  # Pixels per second (faster)
        self.vision_speed_y = 45  # Pixels per second (faster)
        self.vision_direction_x = 1  # 1 for right, -1 for left
        self.vision_direction_y = 1  # 1 for down, -1 for up
        self.vision_min_x = 250
        self.vision_max_x = 950
        self.vision_min_y = 250
        self.vision_max_y = 450
        
        # Negotiation mini-game state
        self.in_negotiation = False
        self.negotiation_timer = 0.0
        self.negotiation_duration = 3.0  # 3 seconds to complete
        self.negotiation_target_npc = None
        self.negotiation_keys_pressed = []
        self.negotiation_sequence = []  # Random sequence of keys to press
        self.negotiation_current_index = 0
        
        # Naughty corner state
        self.in_naughty_corner = False
        self.naughty_corner_timer = 0.0
        self.naughty_corner_duration = 5.0  # 5 seconds penalty
        self.naughty_corner_pos = pygame.math.Vector2(50, 500)
        self.just_caught = False  # Cooldown to prevent immediate re-catching
        self.catch_cooldown = 1.0  # 1 second cooldown after being caught
        self.catch_cooldown_timer = 0.0

    def process_input(self, events):
        super().process_input(events)
        
        # If in naughty corner or negotiating, player can't move
        if self.in_naughty_corner or self.in_negotiation:
            self.movement = pygame.math.Vector2(0, 0)
        
        # Handle E key for talking to students
        for event in events:
            if event.type == pygame.KEYDOWN:

                # Interacting with NPCs
                if event.key == pygame.K_e and not self.in_naughty_corner and not self.in_negotiation:
                    # Check if player is near any NPC
                    for npc in self.npcs:
                        if not npc["talked"]:  # Only talk to NPCs we haven't talked to yet
                            distance = (self.player_pos - npc["pos"]).length()
                            if distance < self.interaction_radius:
                                # Start negotiation mini-game
                                self.in_negotiation = True
                                self.negotiation_target_npc = npc
                                self.negotiation_timer = 0.0
                                self.negotiation_current_index = 0
                                self.negotiation_keys_pressed = []
                                # Generate random sequence: 3-5 arrow keys
                                self.negotiation_sequence = random.choices(
                                    [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
                                    k=random.randint(3, 5)
                                )
                                break
                
                
                # Handle negotiation input
                if self.in_negotiation and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if event.key == self.negotiation_sequence[self.negotiation_current_index]:
                        self.negotiation_current_index += 1
                        if self.negotiation_current_index >= len(self.negotiation_sequence):
                            # Success so add a buyer
                            self.save["buyers"] += 1
                            if self.negotiation_target_npc:
                                self.negotiation_target_npc["talked"] = True
                            self.in_negotiation = False
                            self.negotiation_target_npc = None
                            self.save_game()  # Save buyers immediately
                    else:
                        # Wrong key so negotiation failed
                        self.in_negotiation = False
                        self.negotiation_target_npc = None
                        self.negotiation_current_index = 0

    def update(self, dt):
        super().update(dt)
        
        self.update_negotiation_timer(dt)
        self.update_catch_timer(dt)
        self.update_naughty_corner_timer(dt)
        self.update_vision_circle_status(dt)
        
        # Only allow movement if not in naughty corner and not negotiating
        if not self.in_naughty_corner and not self.in_negotiation:
            super().move(dt)

    def render(self, screen):
        super().render(screen, "Classroom")
        
        self.draw_characters(screen)
        self.draw_teacher_vision(screen)
        self.draw_negotiation(screen)
        self.draw_naughty_corner(screen)
        self.draw_inventory(screen)
        self.draw_clock(screen)
    
    def update_negotiation_timer(self, dt):
        # Update negotiation timer
        if self.in_negotiation:
            self.negotiation_timer += dt
            if self.negotiation_timer >= self.negotiation_duration:
                # Time ran out so negotiation failed
                self.in_negotiation = False
                self.negotiation_target_npc = None
                self.negotiation_current_index = 0
    
    def update_catch_timer(self, dt):
        # Update catch cooldown
        if self.just_caught:
            self.catch_cooldown_timer += dt
            if self.catch_cooldown_timer >= self.catch_cooldown:
                self.just_caught = False
                self.catch_cooldown_timer = 0.0
                
    def update_naughty_corner_timer(self, dt):
        # Update naughty corner timer
        if self.in_naughty_corner:
            self.naughty_corner_timer += dt
            if self.naughty_corner_timer >= self.naughty_corner_duration:
                self.in_naughty_corner = False
                self.naughty_corner_timer = 0.0
                # Return player to a safe position
                self.player_pos = pygame.math.Vector2(600, 400)
                self.player_collision_box.x = self.player_pos.x
                self.player_collision_box.y = self.player_pos.y
                # Start cooldown to prevent immediate re-catching
                self.just_caught = True
                self.catch_cooldown_timer = 0.0
        else:
            # Update teacher's vision circle which is a zig-zag pattern (always moving, even during negotiation)
            self.vision_x += self.vision_speed_x * self.vision_direction_x * dt
            self.vision_y += self.vision_speed_y * self.vision_direction_y * dt
            
            # Bounce at X boundaries
            if self.vision_x >= self.vision_max_x:
                self.vision_x = self.vision_max_x
                self.vision_direction_x = -1
            elif self.vision_x <= self.vision_min_x:
                self.vision_x = self.vision_min_x
                self.vision_direction_x = 1
            
            # Bounce at Y boundaries (zig-zag)
            if self.vision_y >= self.vision_max_y:
                self.vision_y = self.vision_max_y
                self.vision_direction_y = -1
            elif self.vision_y <= self.vision_min_y:
                self.vision_y = self.vision_min_y
                self.vision_direction_y = 1
        
    def update_vision_circle_status(self, dt):
        # Check if player is caught in vision circle (can be caught even during negotiation)
        if not self.in_naughty_corner and not self.just_caught:
            vision_center = pygame.math.Vector2(self.vision_x, self.vision_y)
            distance_to_vision = (self.player_pos - vision_center).length()
            
            if distance_to_vision < self.vision_radius:
                # Player caught! Send to naughty corner
                self.in_naughty_corner = True
                self.naughty_corner_timer = 0.0
                self.player_pos = self.naughty_corner_pos.copy()
                self.player_collision_box.x = self.player_pos.x
                self.player_collision_box.y = self.player_pos.y
                # Lose time (add 30 seconds to timer, making less time remaining)
                self.timer += 30

    def draw_characters(self, screen):
        # Draw player (Andrew)
        andrew_rect = self.andrew_sprite.get_rect(center=self.player_pos)
        screen.blit(self.andrew_sprite, andrew_rect)
        
        # Draw NPCs next to desks
        for npc in self.npcs:
            npc_rect = npc["sprite"].get_rect(center=npc["pos"])
            screen.blit(npc["sprite"], npc_rect)
            
            # Draw interaction indicator if close enough and not talked to
            if not npc["talked"] and not self.in_negotiation:
                distance = (self.player_pos - npc["pos"]).length()
                if distance < self.interaction_radius:
                    # Draw "Press E" hint
                    hint_text = self.font.render("Press E to talk", True, (255, 255, 0))
                    hint_rect = hint_text.get_rect(center=(npc["pos"].x, npc["pos"].y - 30))
                    screen.blit(hint_text, hint_rect)
        
        # Draw teacher at main desk
        teacher_rect = self.teacher_sprite.get_rect(center=self.teacher_pos)
        screen.blit(self.teacher_sprite, teacher_rect)
        
    def draw_teacher_vision(self, screen):
        # Draw teacher's vision circle (semi-transparent red) in a zig-zag pattern
        vision_surface = pygame.Surface((self.vision_radius * 2, self.vision_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(vision_surface, (255, 0, 0, 100), (self.vision_radius, self.vision_radius), self.vision_radius)
        vision_rect = vision_surface.get_rect(center=(self.vision_x, self.vision_y))
        screen.blit(vision_surface, vision_rect)
        
        # Draw vision circle outline
        pygame.draw.circle(screen, (255, 0, 0), (int(self.vision_x), int(self.vision_y)), self.vision_radius, 3)

    def draw_negotiation(self, screen):
        # Draw negotiation mini-game UI
        if self.in_negotiation:
            # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Negotiation box
            box_w, box_h = 500, 300
            box_x = (screen.get_width() - box_w) // 2
            box_y = (screen.get_height() - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (50, 50, 50), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 3)
            
            # Instructions
            inst_text = self.font.render("Press the arrow keys in sequence!", True, (255, 255, 255))
            inst_rect = inst_text.get_rect(center=(box_x + box_w // 2, box_y + 50))
            screen.blit(inst_text, inst_rect)
            
            # Show sequence with text labels instead of emojis
            seq_text = "Sequence: "
            for i, key in enumerate(self.negotiation_sequence):
                if i < self.negotiation_current_index:
                    seq_text += "[OK] "
                else:
                    key_name = {
                        pygame.K_UP: "UP",
                        pygame.K_DOWN: "DOWN", 
                        pygame.K_LEFT: "LEFT",
                        pygame.K_RIGHT: "RIGHT"
                    }
                    seq_text += "[" + key_name.get(key, "?") + "] "
            
            seq_surface = self.font.render(seq_text, True, (255, 255, 0))
            seq_rect = seq_surface.get_rect(center=(box_x + box_w // 2, box_y + 120))
            screen.blit(seq_surface, seq_rect)
            
            # Additional instruction text
            help_text = "Press the arrow keys in the order shown above"
            help_surface = self.small_font.render(help_text, True, (200, 200, 200))
            help_rect = help_surface.get_rect(center=(box_x + box_w // 2, box_y + 150))
            screen.blit(help_surface, help_rect)
            
            # Timer
            time_left = self.negotiation_duration - self.negotiation_timer
            timer_text = self.font.render(f"Time: {time_left:.1f}s", True, (255, 255, 255))
            timer_rect = timer_text.get_rect(center=(box_x + box_w // 2, box_y + 180))
            screen.blit(timer_text, timer_rect)
            
    def draw_naughty_corner(self, screen):
        if self.in_naughty_corner:
            warning_text = self.font.render("NAUGHTY CORNER! Wait...", True, (255, 0, 0))
            warning_rect = warning_text.get_rect(center=(screen.get_width() // 2, 100))
            screen.blit(warning_text, warning_rect)
            
            time_left = self.naughty_corner_duration - self.naughty_corner_timer
            timer_text = self.font.render(f"Time remaining: {time_left:.1f}s", True, (255, 255, 0))
            timer_rect = timer_text.get_rect(center=(screen.get_width() // 2, 140))
            screen.blit(timer_text, timer_rect)