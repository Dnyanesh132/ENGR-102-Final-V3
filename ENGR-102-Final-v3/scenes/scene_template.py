import pygame
from save_manager import load_save, save_data

class Scene:
    """This is the parent class for all scenes, it is like a template.
    """
    
    def __init__(self, duration = None, next_scene_key = None):
        """Default constructor. It sets the initial values for the scene like initial position.

        Parameters:
            duration (float): Time the scene should last in seconds (real time). Defaults to None.
            next_scene_key (string): The key for the scene to follow after the current scene. Defaults to None.
        """
        self.next_scene = self
        self.timer = 0.0
        self.duration = duration
        self.default_next_scene = next_scene_key
        self.font = pygame.font.Font(None, 36)
        self.save = load_save()
        
        # Default data to be changed in other files
        self.player_pos = None
        self.player_collision_box = None
        self.player_speed = None
        self.collision_boxes = None
        
        # Persistent inventory system
        self.show_inventory = False
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)
        
    def save_game(self):
        """When called, saves the game data to the file "save.json".
        """
        save_data(self.save)

    def process_input(self, events):
        """This function detects and defines how input should be processed.

        Parameters:
            events (List[Event]): A list of events that pygame registers at an instant of time.
        """
        self.movement = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()  # continuous input
        if keys[pygame.K_LEFT]:
            self.movement.x = -1
        if keys[pygame.K_RIGHT]:
            self.movement.x = 1
        if keys[pygame.K_UP]:
            self.movement.y = -1
        if keys[pygame.K_DOWN]:
            self.movement.y = 1
        
        # Toggle inventory with I key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
    
    def update(self, dt):
        """This function handles the game logic on what should be updated. It should move objects, animate sprites, check for collisions,
        update timers, update counters, etc.

        Parameters:
            dt (float): The time step (in seconds) taken before updating data again
        """
        # Update the timer
        if self.duration is not None:
            self.timer += dt
            if self.timer >= self.duration and self.default_next_scene:
                self.switch_to(self.default_next_scene)
                
        # Normalize movement speed
        if self.movement.length_squared() > 0:
            self.movement = self.movement.normalize()
            
    def move(self, dt):
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

        self.player_pos.update(self.player_collision_box.x, self.player_collision_box.y)
            
    def render(self, screen):
        """This function is what draws the whole frame to the screen. It does not handle any game logic, it purely draws the pixels to the
        screen without changing anything, completely visual.

        Parameters:
            screen (Surface): The window that displays the game.
        """
        screen.fill((0,0,0))   # Clears the screen

    def display_counters(self, screen):
        WHITE = (255, 255, 255)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        padding = 10
        line1_surface = self.font.render(f"Buyers: {self.save["buyers"]}", True, WHITE)
        line1_rect = line1_surface.get_rect()
        line1_rect.topright = (SCREEN_WIDTH - padding, padding)
        screen.blit(line1_surface, line1_rect)

        line2_surface = self.font.render(f"Cash: {self.save["money"]}", True, WHITE)
        line2_rect = line2_surface.get_rect()
        line2_rect.topright = line1_rect.bottomright
        line2_rect.top += padding
        screen.blit(line2_surface, line2_rect)

        line3_surface = self.font.render(f"Candy: {self.save["candy"]}", True, WHITE)
        line3_rect = line3_surface.get_rect()
        line3_rect.topright = line2_rect.bottomright
        line3_rect.top += padding
        screen.blit(line3_surface, line3_rect)
    
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
    
    def switch_to(self, next_scene_key):
        """This function is used to change what the next scene should be. It is simple enough that it is not overloaded in the individual
        scenes and is defined in the parent class SceneTemplate.

        Parameters:
            next_scene_key (string): The key to the next scene to switch to.
        """
        self.next_scene = next_scene_key