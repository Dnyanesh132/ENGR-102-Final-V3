import pygame
from .scene_template import Scene
from save_manager import load_save

class costco(Scene):
    def __init__(self):
        # Load save first to get remaining time before calling super().__init__()
        save_data = load_save()
        remaining_time = save_data.get("brother_b_remaining_time", 180)
        
        # Initialize the scene - 3 PM to 6 PM continues (remaining time from 180 seconds total)
        # Costco scene gets the remaining time from street scene
        super().__init__(remaining_time, "brother_a_transition")  # After costco, show transition then go to classroom
        
        # Clear the remaining time flag
        if "brother_b_remaining_time" in self.save:
            del self.save["brother_b_remaining_time"]
            self.save_game()
        
        # Initial player position
        self.player_pos = pygame.math.Vector2(200, 500)
        self.player_collision_box = pygame.Rect(self.player_pos.x, self.player_pos.y, 50, 60)
        self.player_speed = self.save.get("bB_speed", 400.0)
        
        # Load Mark's sprite
        try:
            mark_original = pygame.image.load("assets/mark.png").convert_alpha()
            mark_width, mark_height = mark_original.get_size()
            mark_scale = 60 / mark_height
            self.mark_sprite = pygame.transform.scale(mark_original, (int(mark_width * mark_scale), 60))
        except:
            # Fallback to guy_npc if mark.png doesn't exist
            guy_npc_original = pygame.image.load("assets/guy_npc.png").convert_alpha()
            guy_width, guy_height = guy_npc_original.get_size()
            guy_scale = 60 / guy_height
            self.mark_sprite = pygame.transform.scale(guy_npc_original, (int(guy_width * guy_scale), 60))
        
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
        self.in_ps5_menu = False
        self.buy_quantity = 1
        
        # Candy prices (bulk buy prices - cheaper!)
        self.candy_prices = {
            "twizzlers": 0.50,  # Buy for $0.50 (bulk deal)
            "Skizzles": 3,      # Buy for $3 (bulk deal)
            "woozers": 20       # Buy for $20 (bulk deal)
        }
        
        # PS5
        self.ps5_pos = pygame.math.Vector2(600, 200)
        self.ps5_cost = 500
        
        # Interaction radius
        self.interaction_radius = 80
        
        # Max candy capacity
        self.max_candy_capacity = 50  # Default
        if self.save.get("has_bigger_backpack", False):
            self.max_candy_capacity = 200  # Increased with bigger backpack
        
        # Collision boxes - Costco boundaries and obstacles
        self.collision_boxes = [
            # Screen boundaries
            pygame.Rect(-1, 0, 1, 720),
            pygame.Rect(0, -1, 1280, 1),
            pygame.Rect(1280, 0, 1, 720),
            pygame.Rect(0, 720, 1280, 1),
            # Costco shelves/obstacles
            pygame.Rect(100, 300, 200, 100),   # Left shelf
            pygame.Rect(400, 300, 200, 100),   # Middle shelf
            pygame.Rect(700, 300, 200, 100),   # Right shelf
            # Checkout counter (can't walk through it)
            pygame.Rect(850, 350, 300, 100),   # Checkout counter
            # Shop keepers (small collision boxes)
            pygame.Rect(920, 280, 60, 60),     # Shopkeeper 1
            pygame.Rect(1020, 280, 60, 60),    # Shopkeeper 2
            # PS5 display
            pygame.Rect(550, 150, 100, 100),   # PS5 display
        ]
        
        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
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
                    elif not self.in_buy_menu and not self.in_ps5_menu:
                        # Check if near PS5
                        dist_ps5 = (self.player_pos - self.ps5_pos).length()
                        if dist_ps5 < self.interaction_radius:
                            self.in_ps5_menu = True
                
                # Buy menu controls
                if self.in_buy_menu:
                    if event.key == pygame.K_1:
                        self._buy_candy("twizzlers", self.candy_prices["twizzlers"])
                    elif event.key == pygame.K_2:
                        self._buy_candy("Skizzles", self.candy_prices["Skizzles"])
                    elif event.key == pygame.K_3:
                        self._buy_candy("woozers", self.candy_prices["woozers"])
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.buy_quantity = min(20, self.buy_quantity + 1)  # Can buy more in bulk
                    elif event.key == pygame.K_MINUS:
                        self.buy_quantity = max(1, self.buy_quantity - 1)
                    elif event.key == pygame.K_ESCAPE:
                        self.in_buy_menu = False
                        self.at_checkout = False
                        self.checkout_shopkeeper = None
                        return  # Prevent ESC from propagating
                
                # PS5 menu controls
                if self.in_ps5_menu:
                    if event.key == pygame.K_y:
                        self._buy_ps5()
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        self.in_ps5_menu = False
                        return  # Prevent ESC from propagating
                # Skip time is handled in base Scene class now
        
        # Disable movement when in menu
        if self.in_buy_menu or self.in_ps5_menu:
            self.movement = pygame.math.Vector2(0, 0)
    
    def _buy_candy(self, candy_type, price):
        """Buy candy from Costco (bulk prices)"""
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
    
    def _buy_ps5(self):
        """Buy the PS5 which ends the game!"""
        if self.save.get("has_ps5", False):
            return  # Already purchased
        
        if self.save["money"] >= self.ps5_cost:
            self.save["money"] -= self.ps5_cost
            self.save["has_ps5"] = True
            self.save_game()
            # Switch to ending scene
            self.switch_to("ending")
    
    def update(self, dt):
        super().update(dt)
        
        # Only allow movement if not in menu
        if not self.in_buy_menu and not self.in_ps5_menu:
            super().move(dt)
    
    def render(self, screen):
        super().render(screen)
        
        # Load Costco background
        try:
            background_image = pygame.image.load("assets/costco.jpg").convert_alpha()
            background_image = pygame.transform.scale(background_image, screen.get_size())
            screen.blit(background_image, (0, 0))
        except:
            # Fallback Costco background
            screen.fill((200, 50, 50))  # Red Costco color
            # Draw warehouse shelves
            for x in range(100, 1000, 300):
                pygame.draw.rect(screen, (100, 100, 100), (x, 300, 200, 150))
        
        # Draw screen control hints
        super().screen_hints(screen)
        
        # Draw checkout area (register)
        checkout_rect = pygame.Rect(850, 350, 300, 100)
        pygame.draw.rect(screen, (100, 100, 100), checkout_rect)
        pygame.draw.rect(screen, (255, 255, 255), checkout_rect, 3)
        
        # Draw "COSTCO CHECKOUT" text
        checkout_text = self.small_font.render("COSTCO CHECKOUT", True, (255, 255, 255))
        checkout_text_rect = checkout_text.get_rect(center=checkout_rect.center)
        screen.blit(checkout_text, checkout_text_rect)
        
        # Draw shop keepers at checkout
        shopkeeper1_rect = self.shopkeeper1_sprite.get_rect(center=self.shopkeeper1_pos)
        screen.blit(self.shopkeeper1_sprite, shopkeeper1_rect)
        
        shopkeeper2_rect = self.shopkeeper2_sprite.get_rect(center=self.shopkeeper2_pos)
        screen.blit(self.shopkeeper2_sprite, shopkeeper2_rect)
        
        # Draw PS5 display
        ps5_rect = pygame.Rect(self.ps5_pos.x - 50, self.ps5_pos.y - 50, 100, 100)
        pygame.draw.rect(screen, (0, 0, 0), ps5_rect)
        pygame.draw.rect(screen, (255, 255, 0), ps5_rect, 4)
        ps5_text = self.small_font.render("PS5", True, (255, 255, 255))
        ps5_text_rect = ps5_text.get_rect(center=ps5_rect.center)
        screen.blit(ps5_text, ps5_text_rect)
        
        # Draw player (Mark)
        mark_rect = self.mark_sprite.get_rect(center=self.player_pos)
        screen.blit(self.mark_sprite, mark_rect)
        
        # Draw interaction hints
        if not self.in_buy_menu and not self.in_ps5_menu:
            # Checkout hint
            dist1 = (self.player_pos - self.shopkeeper1_pos).length()
            dist2 = (self.player_pos - self.shopkeeper2_pos).length()
            if dist1 < self.interaction_radius or dist2 < self.interaction_radius:
                hint_text = "Press E - Buy Candy (Bulk Deals!)"
                hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                hint_rect = hint_surface.get_rect(center=(screen.get_width() // 2, 100))
                screen.blit(hint_surface, hint_rect)
            
            # PS5 hint
            dist_ps5 = (self.player_pos - self.ps5_pos).length()
            if dist_ps5 < self.interaction_radius:
                if not self.save.get("has_ps5", False):
                    ps5_hint = f"Press E - Buy PS5 (${self.ps5_cost})"
                    ps5_hint_surface = self.small_font.render(ps5_hint, True, (255, 255, 0))
                    ps5_hint_rect = ps5_hint_surface.get_rect(center=(self.ps5_pos.x, self.ps5_pos.y - 80))
                    screen.blit(ps5_hint_surface, ps5_hint_rect)
                else:
                    ps5_hint = "PS5 (Owned)"
                    ps5_hint_surface = self.small_font.render(ps5_hint, True, (0, 255, 0))
                    ps5_hint_rect = ps5_hint_surface.get_rect(center=(self.ps5_pos.x, self.ps5_pos.y - 80))
                    screen.blit(ps5_hint_surface, ps5_hint_rect)
        
        # Draw buy menu
        if self.in_buy_menu:
            # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Buy menu box
            box_w, box_h = 700, 500
            box_x = (screen.get_width() - box_w) // 2
            box_y = (screen.get_height() - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (50, 50, 50), box_rect)
            pygame.draw.rect(screen, (255, 0, 0), box_rect, 4)  # Red border for Costco
            
            # Title
            title_text = "COSTCO - BULK CANDY DEALS"
            title_surface = self.font.render(title_text, True, (255, 215, 0))
            title_rect = title_surface.get_rect(center=(box_x + box_w // 2, box_y + 40))
            screen.blit(title_surface, title_rect)
            
            # Current inventory
            current_total = sum(self.save["candy"].values())
            capacity_text = f"Inventory: {current_total} / {self.max_candy_capacity}"
            capacity_surface = self.small_font.render(capacity_text, True, (255, 255, 255))
            capacity_rect = capacity_surface.get_rect(center=(box_x + box_w // 2, box_y + 80))
            screen.blit(capacity_surface, capacity_rect)
            
            y_offset = box_y + 130
            # Candy options (bulk prices)
            candies = [
                ("1", "Twizzles", "twizzlers", self.candy_prices["twizzlers"], "$2"),
                ("2", "Skizzles", "Skizzles", self.candy_prices["Skizzles"], "$9"),
                ("3", "Woozers", "woozers", self.candy_prices["woozers"], "$40"),
            ]
            
            for key, name, candy_key, buy_price, sell_price in candies:
                candy_text = f"[{key}] {name} - Buy: ${buy_price:.2f} | Sell: {sell_price}"
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
            
            # Instructions
            inst_text = "Press 1-3 to buy, ESC to close"
            inst_surface = self.small_font.render(inst_text, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(center=(box_x + box_w // 2, box_y + box_h - 30))
            screen.blit(inst_surface, inst_rect)
        
        # Draw PS5 purchase menu
        if self.in_ps5_menu:
            # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # PS5 menu box
            box_w, box_h = 600, 400
            box_x = (screen.get_width() - box_w) // 2
            box_y = (screen.get_height() - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (30, 30, 30), box_rect)
            pygame.draw.rect(screen, (255, 255, 0), box_rect, 5)
            
            # Title
            title_text = "PLAYSTATION 5"
            title_surface = self.large_font.render(title_text, True, (255, 255, 0))
            title_rect = title_surface.get_rect(center=(box_x + box_w // 2, box_y + 60))
            screen.blit(title_surface, title_rect)
            
            # Price
            price_text = f"Price: ${self.ps5_cost}"
            price_surface = self.large_font.render(price_text, True, (255, 255, 255))
            price_rect = price_surface.get_rect(center=(box_x + box_w // 2, box_y + 140))
            screen.blit(price_surface, price_rect)
            
            # Current money
            money_text = f"Your Money: ${self.save['money']}"
            money_surface = self.font.render(money_text, True, (200, 200, 200))
            money_rect = money_surface.get_rect(center=(box_x + box_w // 2, box_y + 200))
            screen.blit(money_surface, money_rect)
            
            # Warning
            if self.save["money"] >= self.ps5_cost:
                warning_text = "Buying this will END THE GAME!"
                warning_surface = self.font.render(warning_text, True, (255, 0, 0))
                warning_rect = warning_surface.get_rect(center=(box_x + box_w // 2, box_y + 260))
                screen.blit(warning_surface, warning_rect)
            
            # Buy prompt
            buy_text = "Buy PS5? [Y] Yes  [N] No"
            buy_surface = self.font.render(buy_text, True, (255, 255, 0))
            buy_rect = buy_surface.get_rect(center=(box_x + box_w // 2, box_y + 320))
            screen.blit(buy_surface, buy_rect)
        
        # Draw countdown clock
        time_remaining = self.duration - self.timer
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        clock_text = f"Time: {minutes:02d}:{seconds:02d}"
        clock_surface = self.font.render(clock_text, True, (255, 255, 255))
        clock_rect = clock_surface.get_rect(bottomright=(screen.get_width() - 20, screen.get_height() - 20))
        clock_bg = pygame.Rect(clock_rect.x - 10, clock_rect.y - 5, clock_rect.width + 20, clock_rect.height + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), clock_bg)
        pygame.draw.rect(screen, (255, 255, 255), clock_bg, 2)
        screen.blit(clock_surface, clock_rect)
        
        # Draw UI text
        text = self.font.render("Costco", True, (0, 0, 0))
        screen.blit(text, (20, 20))
        
        # Control hints are now drawn in base Scene class
        
        self.display_counters(screen)
        
        # Draw persistent inventory if toggled
        self.draw_inventory(screen)
