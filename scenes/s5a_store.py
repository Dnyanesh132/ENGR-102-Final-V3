import pygame
from .scene_template import Scene

class store(Scene):
    def __init__(self):
        # Initial player position
        initial_pos = pygame.math.Vector2(640, 500)
        super().__init__(180, "brother_a_transition", "store.jpg", "Mark", initial_pos)  # After store, show transition then go to classroom
        
        # Get remaining time
        self.duration = self.save["brother_b_remaining_time"]
        del self.save["brother_b_remaining_time"]
        self.save_game()

        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)

        # Collision boxes - store boundaries and obstacles
        self.collision_boxes = [
            # Screen boundaries
            pygame.Rect(0, 0, 280, 720),
            pygame.Rect(0, 0, 1280, 250),
            pygame.Rect(1000, 0, 250, 720),
            pygame.Rect(0, 600, 1280, 120),

            pygame.Rect(520, 445, 245, 50),
            pygame.Rect(540, 200, 330, 145),
            pygame.Rect(510, 600, 245, 50),
        ]
        
        # Load Mark's sprite
        mark_original = pygame.image.load("assets/mark.png").convert_alpha()
        mark_width, mark_height = mark_original.get_size()
        mark_scale = 60 / mark_height
        self.mark_sprite = pygame.transform.scale(mark_original, (int(mark_width * mark_scale), 60))
        
        # Shop keeper position
        self.shopkeeper_pos = pygame.math.Vector2(800, 300)  # Behind left side of checkout
        
        # Store state
        self.at_checkout = False
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
                    dist = (self.player_pos - self.shopkeeper_pos).length()
                    
                    if dist < self.interaction_radius:
                        self.at_checkout = True
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
        # Draw mark
        mark_rect = self.mark_sprite.get_rect(center=self.player_pos)
        screen.blit(self.mark_sprite, mark_rect)

    def draw_candy_machine(self, screen):
        # Draw candy machine
        machine_original = pygame.image.load("assets/candy_machine.png").convert_alpha()
        machine_width, machine_height = machine_original.get_size()
        machine_scale = 60 / machine_height
        self.machine_sprite = pygame.transform.scale(machine_original, (int(machine_width * machine_scale), 60))

        machine_rect = self.machine_sprite.get_rect(center=pygame.math.Vector2(self.candy_machine_pos.x - 40, self.candy_machine_pos.y - 20))
        screen.blit(self.machine_sprite, machine_rect)
    
    def draw_checkout_hint(self, screen):
        # Checkout hint
            dist = (self.player_pos - self.shopkeeper_pos).length()
            if dist < self.interaction_radius:
                hint_text = "Press E - Buy Candy"
                hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                hint_rect = hint_surface.get_rect(center=(self.shopkeeper_pos.x, self.shopkeeper_pos.y - 60))
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