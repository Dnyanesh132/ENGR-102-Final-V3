import pygame
from save_manager import load_save, save_data

class Scene:
    """This is the parent class for all scenes, it is like a template.
    """
    
    def __init__(self, duration = None, next_scene_key = None, back_name = None, brother_name = None, initial_pos = None):
        """Default constructor. It sets the initial values for the scene like initial position.

        Parameters:
            duration (float): Time the scene should last in seconds (real time). Defaults to None.
            next_scene_key (string): The key for the scene to follow after the current scene. Defaults to None.
            back_name (string): The name of the file for the background for the current scene. Defaults to None.
            brother_name (string): The name of the brother for the current scene. Defaults to None.
            initial_pos (Vector2): The initial position of the player. Defaults to None.
        """
        self.next_scene = self
        self.timer = 0.0
        self.duration = duration
        self.default_next_scene = next_scene_key
        self.background_name = back_name
        self.font = pygame.font.Font(None, 36)
        self.save = load_save()
        self.show_inventory = False
        
        self.player_pos = initial_pos
        
        self.x_offset = 15
        self.y_offset = -15
        
        # Collision box and speed for respective brother
        if(brother_name == "Andrew"):
            self.player_collision_box = pygame.Rect(self.player_pos.x - self.x_offset, self.player_pos.y - self.y_offset, 30, 20)
            self.player_speed = self.save["bA_speed"]
        elif(brother_name == "Mark"):
            self.player_collision_box = pygame.Rect(self.player_pos.x - self.x_offset, self.player_pos.y - self.y_offset, 30, 20)
            self.player_speed = self.save["bB_speed"]
        
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)
        self.collision_boxes = None

    def process_input(self, events):
        """This function detects and defines how input should be processed.

        Parameters:
            events (List[Event]): A list of events that pygame registers at an instant of time.
        """
        
        self.check_movement_keys(events)
        self.check_open_inventory(events)  
    
    def update(self, dt):
        """This function handles the game logic on what should be updated. It should move objects, animate sprites, check for collisions,
        update timers, update counters, etc.

        Parameters:
            dt (float): The time step (in seconds) taken before updating data again
        """
        
        self.update_timer(dt)
            
    def render(self, screen, name_of_scene = None, tool_tips = True):
        """This function is what draws the whole frame to the screen. It does not handle any game logic, it purely draws the pixels to the
        screen without changing anything, completely visual.

        Parameters:
            screen (Surface): The window that displays the game.
        """
        
        # Clear the screen
        screen.fill((0,0,0))
        
        # Display main stuff
        self.display_background(screen)
        
        if(tool_tips):    
            self.display_screen_hints(screen)
            self.display_counters(screen)
            
        self.display_scene_name(screen, name_of_scene)
    
    def switch_to(self, next_scene_key):
        """This function is used to change what the next scene should be. It is simple enough that it is not overloaded in the individual
        scenes and is defined in the parent class SceneTemplate.

        Parameters:
            next_scene_key (string): The key to the next scene to switch to.
        """
        self.next_scene = next_scene_key
        
    def save_game(self):
        """When called, saves the game data to the file "save.json".
        """
        save_data(self.save)
    
    def check_movement_keys(self,events):
        self.movement = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.movement.x = -1
        if keys[pygame.K_RIGHT]:
            self.movement.x = 1
        if keys[pygame.K_UP]:
            self.movement.y = -1
        if keys[pygame.K_DOWN]:
            self.movement.y = 1
    
    def check_open_inventory(self, events):
        # Toggle inventory with I key, skip time with period key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                elif event.key == pygame.K_PERIOD:
                    # Skip 15 seconds (for debugging)
                    if self.duration is not None:
                        self.timer += 15
        
    def update_timer(self, dt):
        if self.duration is not None:
            self.timer += dt
            if self.timer >= self.duration and self.default_next_scene:
                self.switch_to(self.default_next_scene)
            
    def move(self, dt):
        # Normalize movement speed
        if self.movement.length_squared() > 0:
            self.movement = self.movement.normalize()
            
        # Check if a collision occurs in either x or y direction before updating movement
        if self.movement.x != 0:
            new_rect = self.player_collision_box.copy()
            new_rect.x += self.movement.x * self.player_speed * dt

            if not any(new_rect.colliderect(box) for box in self.collision_boxes):
                self.player_collision_box.x = new_rect.x

        if self.movement.y != 0:
            new_rect = self.player_collision_box.copy()
            new_rect.y += self.movement.y * self.player_speed * dt

            if not any(new_rect.colliderect(box) for box in self.collision_boxes):
                self.player_collision_box.y = new_rect.y

        # Update position
        self.player_pos.update(self.player_collision_box.x + self.x_offset, self.player_collision_box.y + self.y_offset)
        
    def display_background(self, screen):
        # Load background if necessary
        if(self.background_name != None):
            background_image = pygame.image.load("assets/backgrounds/" + self.background_name).convert_alpha()
            background_image = pygame.transform.scale(background_image, screen.get_size())
            screen.blit(background_image, (0, 0))
        
    def display_screen_hints(self, screen):
        # Draw persistent control hints (shown everywhere)
        hints_y = 670
        hint_bg = pygame.Rect(10, hints_y - 5, 350, 40)
        hint_surface = pygame.Surface((hint_bg.width, hint_bg.height), pygame.SRCALPHA)
        hint_surface.fill((0, 0, 0, 150))
        screen.blit(hint_surface, hint_bg)
        
        controls_text = "[.] Fast Forward 15s  |  [I] Inventory"
        controls_surface = self.small_font.render(controls_text, True, (200, 200, 255))
        screen.blit(controls_surface, (20, hints_y))

    def display_counters(self, screen):
        COLOR = (0, 0, 0)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        padding = 10
        line1_surface = self.font.render(f"Buyers: {self.save["buyers"]}", True, COLOR)
        line1_rect = line1_surface.get_rect()
        line1_rect.topright = (SCREEN_WIDTH - padding, padding)
        screen.blit(line1_surface, line1_rect)

        line2_surface = self.font.render(f"Cash: {self.save["money"]}", True, COLOR)
        line2_rect = line2_surface.get_rect()
        line2_rect.topright = line1_rect.bottomright
        line2_rect.top += padding
        screen.blit(line2_surface, line2_rect)
    
    def display_scene_name(self, screen, scene_name):
        if(scene_name != None):
            text = self.font.render(scene_name, True, (0,0,0))
            screen.blit(text, (20, 20))
        
    def draw_inventory(self, screen):
        """Draw persistent inventory that shows candies and items"""
        if not self.show_inventory:
            return
        
        # Create inventory box (centered on screen)
        inv_box = pygame.Rect(200, 100, 880, 520)
        inv_surface = pygame.Surface((inv_box.width, inv_box.height), pygame.SRCALPHA)
        inv_surface.fill((0, 0, 0, 220))
        screen.blit(inv_surface, inv_box)
        pygame.draw.rect(screen, (255, 215, 0), inv_box, 4)
        
        # Title
        title_text = pygame.font.Font(None, 50).render("INVENTORY", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(inv_box.centerx, inv_box.y + 30))
        screen.blit(title_text, title_rect)
        
        # Close hint
        close_text = self.tiny_font.render("Press [I] to close", True, (200, 200, 200))
        close_rect = close_text.get_rect(center=(inv_box.centerx, inv_box.bottom - 20))
        screen.blit(close_text, close_rect)
        
        y_offset = inv_box.y + 80
        
        # Candy section
        candy_title = self.font.render("CANDY:", True, (255, 255, 255))
        screen.blit(candy_title, (inv_box.x + 30, y_offset))
        y_offset += 40
        
        candy = self.save.get("candy", {})
        twizzles = candy.get("twizzlers", 0)
        skizzles = candy.get("Skizzles", 0)
        woozers = candy.get("woozers", 0)
        
        twizzles_text = f"  Twizzles: {twizzles}"
        twizzles_surface = self.small_font.render(twizzles_text, True, (255, 255, 255))
        screen.blit(twizzles_surface, (inv_box.x + 50, y_offset))
        y_offset += 35
        
        skizzles_text = f"  Skizzles: {skizzles}"
        skizzles_surface = self.small_font.render(skizzles_text, True, (255, 255, 255))
        screen.blit(skizzles_surface, (inv_box.x + 50, y_offset))
        y_offset += 35
        
        woozers_text = f"  Woozers: {woozers}"
        woozers_surface = self.small_font.render(woozers_text, True, (255, 255, 255))
        screen.blit(woozers_surface, (inv_box.x + 50, y_offset))
        y_offset += 60
        
        # Items section
        items_title = self.font.render("ITEMS:", True, (255, 255, 255))
        screen.blit(items_title, (inv_box.x + 30, y_offset))
        y_offset += 40
        
        # Check for purchased items
        items = []
        if self.save.get("has_costco_membership", False):
            items.append("Costco Membership")
        if self.save.get("has_bicycle", False):
            items.append("Bicycle")
        if self.save.get("has_candy_machine", False):
            items.append("Candy Machine")
        if self.save.get("has_bigger_backpack", False):
            items.append("Bigger Backpack")
        
        if items:
            for item in items:
                item_text = f"  {item}"
                item_surface = self.small_font.render(item_text, True, (150, 255, 150))
                screen.blit(item_surface, (inv_box.x + 50, y_offset))
                y_offset += 35
        else:
            no_items_text = "  No items purchased yet"
            no_items_surface = self.small_font.render(no_items_text, True, (150, 150, 150))
            screen.blit(no_items_surface, (inv_box.x + 50, y_offset))
    
    def draw_clock(self, screen):
        # Draw countdown clock (bottom right)
        time_remaining = self.duration - self.timer
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        clock_text = f"Time: {minutes:02d}:{seconds:02d}"
        clock_surface = self.font.render(clock_text, True, (255, 255, 255))
        clock_rect = clock_surface.get_rect(bottomright=(screen.get_width() - 20, screen.get_height() - 20))
        
        # Draw background for clock
        clock_bg = pygame.Rect(clock_rect.x - 10, clock_rect.y - 5, clock_rect.width + 20, clock_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), clock_bg)
        pygame.draw.rect(screen, (255, 255, 255), clock_bg, 2)
        screen.blit(clock_surface, clock_rect)

    def display_collision_boxes(self, screen):
        """Draws all collision boxes and the player's collision box for debugging."""
        
        # Color for the collision boxes (e.g., translucent red)
        COLLISION_COLOR = (255, 0, 0, 100) # (R, G, B, Alpha)
        PLAYER_COLLISION_COLOR = (0, 255, 0, 150) # (R, G, B, Alpha)
        
        # Since pygame.draw.rect doesn't support drawing semi-transparent rectangles directly,
        # we'll use a Surface with SRCALPHA for transparency.
        
        # Create a surface to draw collision boxes on
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Draw all static collision boxes
        if self.collision_boxes:
            for box in self.collision_boxes:
                # Use a transparent color for the static boxes
                pygame.draw.rect(overlay, COLLISION_COLOR, box)
                
        # Draw the player's collision box
        if self.player_collision_box:
            # Use a slightly more opaque/different color for the player
            pygame.draw.rect(overlay, PLAYER_COLLISION_COLOR, self.player_collision_box)
            
        # Blit the overlay onto the main screen
        screen.blit(overlay, (0, 0))