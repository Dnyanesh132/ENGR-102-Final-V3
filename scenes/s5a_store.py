import pygame
from .scene_template import Scene
from save_manager import load_save

class store(Scene):
    def __init__(self):
        # Initial player position
        initial_pos = pygame.math.Vector2(200, 500)
        super().__init__(None, "brother_a_transition", "store.jpg", "Andrew", initial_pos)  # After store, show transition then go to classroom
        
        # Get remaining time
        self.timer = self.save["brother_b_remaining_time"]
        del self.save["brother_b_remaining_time"]
        self.save_game()

        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)

        # Collision boxes - store boundaries and obstacles
        self.collision_boxes = [
            # Screen boundaries
            pygame.Rect(-1, 0, 1, 720),
            pygame.Rect(0, -1, 1280, 1),
            pygame.Rect(1280, 0, 1, 720),
            pygame.Rect(0, 720, 1280, 1),
            # Store shelves/obstacles
            pygame.Rect(100, 200, 200, 100),   # Left shelf
            pygame.Rect(400, 200, 200, 100),   # Middle shelf
            pygame.Rect(700, 200, 200, 100),   # Right shelf
            # Checkout counter (can't walk through it)
            pygame.Rect(850, 350, 300, 100),   # Checkout counter
            # Shop keepers (small collision boxes)
            pygame.Rect(920, 280, 60, 60),     # Shopkeeper 1
            pygame.Rect(1020, 280, 60, 60),   # Shopkeeper 2
            # Candy machine
            pygame.Rect(560, 260, 80, 80),     # Candy machine
        ]
        
        # Load Mark's sprite
        andrew_original = pygame.image.load("assets/andrew.png").convert_alpha()
        andrew_width, andrew_height = andrew_original.get_size()
        andrew_scale = 60 / andrew_height
        self.andrew_sprite = pygame.transform.scale(andrew_original, (int(andrew_width * andrew_scale), 60))
        
        # Load shop keeper sprites (using guy_npc and girl_npc)
        guy_npc_original = pygame.image.load("assets/guy_npc.png").convert_alpha()
        guy_width, guy_height = guy_npc_original.get_size()
        guy_scale = 70 / guy_height
        self.shopkeeper1_sprite = pygame.transform.scale(guy_npc_original, (int(guy_width * guy_scale), 70))
        
        girl_npc_original = pygame.image.load("assets/girl_npc.png").convert_alpha()
        girl_width, girl_height = girl_npc_original.get_size()
        girl_scale = 70 / girl_height
        self.shopkeeper2_sprite = pygame.transform.scale(girl_npc_original, (int(girl_width * girl_scale), 70))
        
        # Shop keeper positions (behind checkout counter, not on it)
        self.shopkeeper1_pos = pygame.math.Vector2(950, 320)  # Behind left side of checkout
        self.shopkeeper2_pos = pygame.math.Vector2(1050, 320)  # Behind right side of checkout
        
        # Store state
        self.at_checkout = False
        self.checkout_shopkeeper = None  # Which shopkeeper (1 or 2)
        self.in_buy_menu = False
        self.buy_quantity = 1
        
        # Candy prices (buy prices)
        self.candy_prices = {
            "twizzlers": 1,  # Buy for $1
            "Skizzles": 5,   # Buy for $5
            "woozers": 30    # Buy for $30
        }
        
        # Candy machine
        self.candy_machine_pos = pygame.math.Vector2(600, 300)
        self.candy_machine_cost = 150
        self.candy_machine_woozers = 5  # Generates 5 woozers
        
        # Interaction radius
        self.interaction_radius = 80
        
        # Max candy capacity
        self.max_candy_capacity = 50  # Default
        if self.save.get("has_bigger_backpack", False):
            self.max_candy_capacity = 200  # Increased with bigger backpack
        
    def process_input(self, events):
        super().process_input(events)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # Check if near checkout
                    dist1 = (self.player_pos - self.shopkeeper1_pos).length()
                    dist2 = (self.player_pos - self.shopkeeper2_pos).length()
                    
                    if dist1 < self.interaction_radius:
                        self.at_checkout = True
                        self.checkout_shopkeeper = 1
                        self.in_buy_menu = True
                    elif dist2 < self.interaction_radius:
                        self.at_checkout = True
                        self.checkout_shopkeeper = 2
                        self.in_buy_menu = True
                    elif not self.in_buy_menu:
                        # Check if near candy machine
                        dist_machine = (self.player_pos - self.candy_machine_pos).length()
                        if dist_machine < self.interaction_radius:
                            self.buy_candy_machine()
                
                # Buy menu controls
                if self.in_buy_menu:
                    if event.key == pygame.K_1:
                        self.buy_candy("twizzlers", self.candy_prices["twizzlers"])
                    elif event.key == pygame.K_2:
                        self.buy_candy("Skizzles", self.candy_prices["Skizzles"])
                    elif event.key == pygame.K_3:
                        self.buy_candy("woozers", self.candy_prices["woozers"])
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.buy_quantity = min(10, self.buy_quantity + 1)  # Increase
                    elif event.key == pygame.K_MINUS:
                        self.buy_quantity = max(1, self.buy_quantity - 1)  # Decrease
                    elif event.key == pygame.K_ESCAPE:
                        self.in_buy_menu = False
                        self.at_checkout = False
                        self.checkout_shopkeeper = None
                        return  # Prevent ESC from propagating
                # Skip time is handled in base Scene class now
        
        # Disable movement when in menu
        if self.in_buy_menu:
            self.movement = pygame.math.Vector2(0, 0)
    
    def update(self, dt):
        super().update(dt)
        
        # Only allow movement if not in menu
        if not self.in_buy_menu:
            super().move(dt)
    
    def render(self, screen):
        super().render(screen, "Store")

        self.draw_characters(screen)
        self.draw_checkout_area(screen)
        self.draw_candy_machine(screen)

        if not self.in_buy_menu:
            self.draw_checkout_hint(screen)
            self.draw_candy_machine_hint(screen)

        self.draw_buy_menu(screen)

        self.draw_clock(screen)
        self.draw_inventory(screen)

    def buy_candy(self, candy_type, price):
        """Buy candy from the store"""
        total_cost = price * self.buy_quantity
        
        # Check if player has enough money
        if self.save["money"] < total_cost:
            return  # Can't afford
        
        # Check current candy count
        current_total = sum(self.save["candy"].values())
        
        # Check if adding this quantity would exceed capacity
        if current_total + self.buy_quantity > self.max_candy_capacity:
            return  # Exceeds capacity
        
        # Buy the candy
        self.save["money"] -= total_cost
        if candy_type not in self.save["candy"]:
            self.save["candy"][candy_type] = 0
        self.save["candy"][candy_type] += self.buy_quantity
        self.save_game()
    
    def buy_candy_machine(self):
        """Buy the candy machine"""
        if self.save.get("has_candy_machine", False):
            return  # Already purchased
        
        if self.save["money"] >= self.candy_machine_cost:
            self.save["money"] -= self.candy_machine_cost
            self.save["has_candy_machine"] = True
            # Generate 5 woozers
            if "woozers" not in self.save["candy"]:
                self.save["candy"]["woozers"] = 0
            self.save["candy"]["woozers"] += self.candy_machine_woozers
            self.save_game()

    def draw_characters(self, screen):
        # Draw Andrew
        andrew_rect = self.andrew_sprite.get_rect(center=self.player_pos)
        screen.blit(self.andrew_sprite, andrew_rect)

        # Draw shop keepers at checkout
        shopkeeper1_rect = self.shopkeeper1_sprite.get_rect(center=self.shopkeeper1_pos)
        screen.blit(self.shopkeeper1_sprite, shopkeeper1_rect)
        
        shopkeeper2_rect = self.shopkeeper2_sprite.get_rect(center=self.shopkeeper2_pos)
        screen.blit(self.shopkeeper2_sprite, shopkeeper2_rect)

    def draw_checkout_area(self, screen):
        # Draw checkout area (register)
        checkout_rect = pygame.Rect(850, 350, 300, 100)
        pygame.draw.rect(screen, (100, 100, 100), checkout_rect)
        pygame.draw.rect(screen, (255, 255, 255), checkout_rect, 3)
        
        # Draw "CHECKOUT" text
        checkout_text = self.small_font.render("CHECKOUT", True, (255, 255, 255))
        checkout_text_rect = checkout_text.get_rect(center=checkout_rect.center)
        screen.blit(checkout_text, checkout_text_rect)

    def draw_candy_machine(self, screen):
        # Draw candy machine
        machine_rect = pygame.Rect(self.candy_machine_pos.x - 40, self.candy_machine_pos.y - 40, 80, 80)
        pygame.draw.rect(screen, (150, 150, 150), machine_rect)
        pygame.draw.rect(screen, (255, 255, 0), machine_rect, 3)
        machine_text = self.tiny_font.render("CANDY", True, (0, 0, 0))
        machine_text_rect = machine_text.get_rect(center=machine_rect.center)
        screen.blit(machine_text, machine_text_rect)
    
    def draw_checkout_hint(self, screen):
        # Checkout hint
            dist1 = (self.player_pos - self.shopkeeper1_pos).length()
            dist2 = (self.player_pos - self.shopkeeper2_pos).length()
            if dist1 < self.interaction_radius or dist2 < self.interaction_radius:
                hint_text = "Press E - Buy Candy"
                hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                hint_rect = hint_surface.get_rect(center=(screen.get_width() // 2, 100))
                screen.blit(hint_surface, hint_rect)

    def draw_candy_machine_hint(self, screen):
        # Candy machine hint
            dist_machine = (self.player_pos - self.candy_machine_pos).length()
            if dist_machine < self.interaction_radius:
                if not self.save.get("has_candy_machine", False):
                    machine_hint = f"Press E - Buy Candy Machine (${self.candy_machine_cost})"
                    machine_hint_surface = self.small_font.render(machine_hint, True, (255, 255, 0))
                    machine_hint_rect = machine_hint_surface.get_rect(center=(self.candy_machine_pos.x, self.candy_machine_pos.y - 60))
                    screen.blit(machine_hint_surface, machine_hint_rect)
                else:
                    machine_hint = "Candy Machine (Owned)"
                    machine_hint_surface = self.small_font.render(machine_hint, True, (0, 255, 0))
                    machine_hint_rect = machine_hint_surface.get_rect(center=(self.candy_machine_pos.x, self.candy_machine_pos.y - 60))
                    screen.blit(machine_hint_surface, machine_hint_rect)
    
    def draw_buy_menu(self, screen):
        # Draw buy menu
        if self.in_buy_menu:
            self.dim_background(screen)
            
            # Dimensions of buy menu
            boxw, boxh = 700, 500
            boxx = (screen.get_width() - boxw) // 2
            boxy = (screen.get_height() - boxh) // 2

            self.draw_menu_box(screen, boxx, boxy, boxw, boxh)
            self.draw_menu_title(screen, boxx, boxy, boxw, boxh)
            self.draw_menu_box(screen, boxx, boxy, boxw, boxh)
            self.draw_curr_inventory(screen, boxx, boxy, boxw, boxh)
            self.draw_menu_instructions(screen, boxx, boxy, boxw, boxh)

    def dim_background(self, screen):
        # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

    def draw_menu_box(self, screen, box_x, box_y, box_w, box_h):
        # Buy menu box
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (50, 50, 50), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 4)

    def draw_menu_title(self, screen, box_x, box_y, box_w, box_h):
        # Title
            title_text = "CANDY STORE - BUY CANDY"
            title_surface = self.font.render(title_text, True, (255, 215, 0))
            title_rect = title_surface.get_rect(center=(box_x + box_w // 2, box_y + 40))
            screen.blit(title_surface, title_rect)

    def draw_curr_inventory(self, screen, box_x, box_y, box_w, box_h):
        # Current inventory
            current_total = sum(self.save["candy"].values())
            capacity_text = f"Inventory: {current_total} / {self.max_candy_capacity}"
            capacity_surface = self.small_font.render(capacity_text, True, (255, 255, 255))
            capacity_rect = capacity_surface.get_rect(center=(box_x + box_w // 2, box_y + 80))
            screen.blit(capacity_surface, capacity_rect)
            
            y_offset = box_y + 130
            # Candy options
            candies = [
                ("1", "Twizzles", "twizzlers", self.candy_prices["twizzlers"], "$2"),
                ("2", "Skizzles", "Skizzles", self.candy_prices["Skizzles"], "$9"),
                ("3", "Woozers", "woozers", self.candy_prices["woozers"], "$40"),
            ]
            
            for key, name, candy_key, buy_price, sell_price in candies:
                candy_text = f"[{key}] {name} - Buy: ${buy_price} | Sell: {sell_price}"
                candy_surface = self.font.render(candy_text, True, (255, 255, 255))
                screen.blit(candy_surface, (box_x + 50, y_offset))
                
                # Current amount
                current = self.save["candy"].get(candy_key, 0)
                current_text = f"  You have: {current}"
                current_surface = self.small_font.render(current_text, True, (200, 200, 200))
                screen.blit(current_surface, (box_x + 50, y_offset + 30))
                
                y_offset += 70
        
        # Quantity selector
            y_offset += 20
            qty_text = f"Quantity: {self.buy_quantity}  [+/-] to change"
            qty_surface = self.font.render(qty_text, True, (255, 255, 0))
            qty_rect = qty_surface.get_rect(center=(box_x + box_w // 2, y_offset))
            screen.blit(qty_surface, qty_rect)

    def draw_menu_instructions(self, screen, box_x, box_y, box_w, box_h):
         # Instructions
            inst_text = "Press 1-3 to buy, ESC to close"
            inst_surface = self.small_font.render(inst_text, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(center=(box_x + box_w // 2, box_y + box_h - 30))
            screen.blit(inst_surface, inst_rect)