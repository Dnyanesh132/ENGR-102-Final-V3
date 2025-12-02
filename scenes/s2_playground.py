import pygame
import random
from .scene_template import Scene

class playground(Scene):
    def __init__(self):
        # Initial player position 
        initial_pos = pygame.math.Vector2(640, 360)
        super().__init__(120, "hallway", "playground.png", "Andrew", initial_pos)  # 11am-1pm = 120 seconds
        
        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 24)
        
        # Collision boxes (playground boundaries - fence at top, blue bar at bottom)
        self.collision_boxes = [
            # Left fence/wall
            pygame.Rect(0, 0, 10, 720),
            # Right fence/wall
            pygame.Rect(1270, 0, 10, 720),
            # Top fence (keep players below fence)
            pygame.Rect(0, 0, 1280, 260),
            
            
            # Bottom blue bar (keep players above blue bar)
            pygame.Rect(0, 630, 1280, 70),
            
            ####playground toys######
            
            #jungle
            #swing
            #trunk
            #playplace
            pygame.Rect(40,250, 180, 80), 
            pygame.Rect(270, 250, 220, 80), 
            pygame.Rect(570, 250, 120, 70), 
            pygame.Rect(800, 250, 380, 75)
            
        
        ]
        
        # Load Sprites
        
        # Load Brother A
        andrew_original = pygame.image.load("assets/andrew.png").convert_alpha()
        andrew_width, andrew_height = andrew_original.get_size()
        andrew_scale = 60 / andrew_height
        self.andrew_sprite = pygame.transform.scale(andrew_original, (int(andrew_width * andrew_scale)/60 * 110, 110))
        
        # Load big bully sprite
        big_bully_original = pygame.image.load("assets/big_bully.png").convert_alpha()
        bully_width, bully_height = big_bully_original.get_size()
        bully_scale = 50 / bully_height
        self.big_bully_sprite = pygame.transform.scale(big_bully_original, (int(bully_width * bully_scale)/50 * 130, 130))
        
        # Load small bully sprite
        small_bully_original = pygame.image.load("assets/snall_bully.png").convert_alpha()
        small_bully_width, small_bully_height = small_bully_original.get_size()
        small_bully_scale = 40 / small_bully_height
        self.small_bully_sprite = pygame.transform.scale(small_bully_original, (int(small_bully_width * small_bully_scale)/40 * 85, 85))
        
        # Load other student npcs
        guy_npc_original = pygame.image.load("assets/guy_npc.png").convert_alpha()
        guy_width, guy_height = guy_npc_original.get_size()
        guy_scale = 45 / guy_height
        self.guy_npc_sprite = pygame.transform.scale(guy_npc_original, (int(guy_width * guy_scale)/45 * 85, 85))
        
        girl_npc_original = pygame.image.load("assets/girl_npc.png").convert_alpha()
        girl_width, girl_height = girl_npc_original.get_size()
        girl_scale = 45 / girl_height
        self.girl_npc_sprite = pygame.transform.scale(girl_npc_original, (int(girl_width * girl_scale)/45 * 85, 85))
        

        # Get number of buyers from classroom negotiations (ensure it persists)
        self.num_buyers = max(0, self.save.get("buyers", 0))  # Ensure it doesn't go negative
        
        # Playground boundaries (grass and sandbox area only)
        # Based on typical playground layout: fence at top, blue bar at bottom
        self.playground_bounds = {
            "left": 50,
            "right": 1230,
            "top": 300,  # Below fence
            "bottom": 600  # Above blue bar (approximately)
        }
        
        # Create buyer positions (randomly scattered on playground) with mix of boy/girl
        self.buyers = []
        for i in range(self.num_buyers):
            x = random.randint(self.playground_bounds["left"] + 50, self.playground_bounds["right"] - 50)
            y = random.randint(300 , 620)
            # Mix of boy and girl NPCs
            is_girl = random.choice([True, False])
            self.buyers.append({
                "pos": pygame.math.Vector2(x, y),
                "sold": False,
                "is_girl": is_girl
            })
        

        # Create random NPCs (non-buyers, just for atmosphere) - max 12 random NPCs
        num_random_npcs = min(12, random.randint(8, 12))
        self.random_npcs = []
        for i in range(num_random_npcs):
            # Spawn within playground bounds (between fence and aqua bar)
            x = random.randint(self.playground_bounds["left"] + 50, self.playground_bounds["right"] - 80)
            y = random.randint(300, 620)
            is_girl = random.choice([True, False])
            self.random_npcs.append({
                "pos": pygame.math.Vector2(x, y),
                "is_girl": is_girl
            })
        

        # Create exactly 8 bullies (mix of big and small)
        num_bullies = 8
        self.bullies = []
        for i in range(num_bullies):
            # Spawn within playground bounds (between fence and aqua bar)
            x = random.randint(self.playground_bounds["left"] + 50, self.playground_bounds["right"] - 50)
            y = random.randint(self.playground_bounds["top"] + 200, self.playground_bounds["bottom"] - 50)
            is_big = random.choice([True, False])  # Mix of big and small
            self.bullies.append({
                "pos": pygame.math.Vector2(x, y),
                "direction": pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize(),
                "speed": 50 if is_big else 60,  # Small bullies slightly faster
                "frozen": False,
                "frozen_timer": 0.0,
                "is_big": is_big
            })
        

        # Selling mechanics
        self.sell_quantity = 1  # Amount to sell per transaction
        self.interaction_radius = 60
        
    def process_input(self, events):
        super().process_input(events)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Selling controls
                if event.key == pygame.K_1:  # Sell Twizzles
                    self.try_sell("twizzlers", 2)  # Sell price $2
                elif event.key == pygame.K_2:  # Sell Skizzles
                    self.try_sell("Skizzles", 9)  # Sell price $9
                elif event.key == pygame.K_3:  # Sell Woozers
                    self.try_sell("woozers", 40)  # Sell price $40
                
                # Quantity controls (max 5 pieces)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.sell_quantity = min(5, self.sell_quantity + 1)
                elif event.key == pygame.K_MINUS:
                    self.sell_quantity = max(1, self.sell_quantity - 1)
                    
    def update(self, dt):
        super().update(dt)
        
        self.update_bully_position(dt)
        
        # Move player
        super().move(dt)
        
    def render(self, screen):
        super().render(screen, "Lunch Break - Playground")
        
        self.draw_characters(screen)
        self.draw_ui(screen)
        self.draw_buyer_hints(screen)
        self.draw_clock(screen)
        self.draw_inventory(screen)
    
    def try_sell(self, candy_type, sell_price):
        """Try to sell candy to a nearby buyer"""
        # Check if player is near any unsold buyer
        for buyer in self.buyers:
            if not buyer["sold"]:
                distance = (self.player_pos - buyer["pos"]).length()
                if distance < self.interaction_radius:
                    # Check inventory (handle different key formats)
                    candy_key = candy_type
                    # Try different possible keys
                    if candy_key.lower() == "twizzlers" or candy_key.lower() == "twizzles":
                        candy_key = "twizzlers"
                    elif candy_key.lower() == "skizzles":
                        candy_key = "Skizzles"
                    elif candy_key.lower() == "woozers":
                        candy_key = "woozers"
                    
                    current_amount = self.save["candy"].get(candy_key, 0)
                    
                    # Check if we have enough candy
                    if current_amount >= self.sell_quantity:
                        # Sell the candy
                        self.save["candy"][candy_key] = current_amount - self.sell_quantity
                        self.save["money"] += sell_price * self.sell_quantity
                        buyer["sold"] = True
                        # Decrease buyer count
                        self.save["buyers"] = max(0, self.save["buyers"] - 1)
                        self.num_buyers = self.save["buyers"]
                        self.save_game()
                        break

    def update_bully_position(self, dt):
        # Update bully movement (keep within playground bounds)
        for bully in self.bullies:
            if not bully["frozen"]:
                # Move bully
                new_pos = bully["pos"] + bully["direction"] * bully["speed"] * dt
                
                # Bounce off playground boundaries
                if new_pos.x < self.playground_bounds["left"] or new_pos.x > self.playground_bounds["right"]:
                    bully["direction"].x *= -1
                    new_pos.x = max(self.playground_bounds["left"], min(self.playground_bounds["right"], new_pos.x))
                if new_pos.y < self.playground_bounds["top"] or new_pos.y > self.playground_bounds["bottom"]:
                    bully["direction"].y *= -1
                    new_pos.y = max(self.playground_bounds["top"], min(self.playground_bounds["bottom"], new_pos.y))
                
                # Normalize direction after bounce
                if bully["direction"].length_squared() > 0:
                    bully["direction"] = bully["direction"].normalize()
                
                bully["pos"] = new_pos
                
                # Check collision with player
                distance = (self.player_pos - bully["pos"]).length()
                if distance < 40:  # Collision radius
                    # Player hit by bully!
                    # Lose 10% of cash (rounded)
                    cash_loss = int(self.save["money"] * 0.1)
                    if cash_loss > 0:
                        self.save["money"] = max(0, self.save["money"] - cash_loss)
                    
                    # Lose 30 seconds
                    self.timer += 30
                    
                    # Freeze bully
                    bully["frozen"] = True
                    bully["frozen_timer"] = 0.0
                    self.save_game()
            else:
                # Update frozen timer (bully stays frozen indefinitely for mercy)
                bully["frozen_timer"] += dt
    
    def draw_characters(self, screen):
        # Draw player (Andrew)
        andrew_rect = self.andrew_sprite.get_rect(center=self.player_pos)
        screen.blit(self.andrew_sprite, andrew_rect)

        # Draw random NPCs (non-buyers, just atmosphere)
        for npc in self.random_npcs:
            npc_sprite = self.girl_npc_sprite if npc["is_girl"] else self.guy_npc_sprite
            npc_rect = npc_sprite.get_rect(center=npc["pos"])
            screen.blit(npc_sprite, npc_rect)
        
        # Draw buyers (highlighted if not sold) - mix of boy/girl
        for buyer in self.buyers:
            if not buyer["sold"]:
                # Draw highlight circle
                pygame.draw.circle(screen, (255, 255, 0), (int(buyer["pos"].x), int(buyer["pos"].y)), 30, 3)
                # Draw buyer sprite (boy or girl)
                buyer_sprite = self.girl_npc_sprite if buyer["is_girl"] else self.guy_npc_sprite
                buyer_rect = buyer_sprite.get_rect(center=buyer["pos"])
                screen.blit(buyer_sprite, buyer_rect)
        
        # Draw bullies (big and small)
        for bully in self.bullies:
            bully_sprite = self.big_bully_sprite if bully["is_big"] else self.small_bully_sprite
            bully_rect = bully_sprite.get_rect(center=bully["pos"])
            screen.blit(bully_sprite, bully_rect)
            if bully["frozen"]:
                # Draw frozen indicator
                frozen_text = self.small_font.render("FROZEN", True, (0, 0, 255))
                frozen_rect = frozen_text.get_rect(center=(bully["pos"].x, bully["pos"].y - 30))
                screen.blit(frozen_text, frozen_rect)
    
    def draw_buyer_hints(self, screen):
        # Show nearby buyer hint
        for buyer in self.buyers:
            if not buyer["sold"]:
                distance = (self.player_pos - buyer["pos"]).length()
                if distance < self.interaction_radius:
                    hint_text = "Press 1/2/3 to sell candy"
                    hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                    hint_rect = hint_surface.get_rect(center=(screen.get_width() // 2, 100))
                    screen.blit(hint_surface, hint_rect)
                    break
        else:
            return
    
    def draw_ui(self, screen):
        """Draw the selling controls UI in a cleaner format"""
        # Create a semi-transparent background box
        ui_box = pygame.Rect(10, 50, 400, 120)
        ui_surface = pygame.Surface((ui_box.width, ui_box.height), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 150))
        screen.blit(ui_surface, ui_box)
        pygame.draw.rect(screen, (255, 255, 255), ui_box, 2)
        
        y_offset = 60
        # Selling controls
        sell_text = "Sell: [1] Twizzles  [2] Skizzles  [3] Woozers"
        sell_surface = self.tiny_font.render(sell_text, True, (255, 255, 255))
        screen.blit(sell_surface, (20, y_offset))
        
        y_offset += 25
        # Quantity controls
        qty_text = f"Quantity: {self.sell_quantity}  [+/-] to change"
        qty_surface = self.tiny_font.render(qty_text, True, (255, 255, 255))
        screen.blit(qty_surface, (20, y_offset))
        
        y_offset += 25
        # Prices
        price_text = "Prices: $2  |  $9  |  $40"
        price_surface = self.tiny_font.render(price_text, True, (200, 200, 200))
        screen.blit(price_surface, (20, y_offset))
    
