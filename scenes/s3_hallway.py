import pygame
from .scene_template import Scene

class hallway(Scene):
    def __init__(self):
        # Initial player position
        initial_pos = pygame.math.Vector2(200, 360)
        super().__init__(120, "brother_b_transition", "hallway.png", "Andrew", initial_pos)  # 1pm-3pm = 120 seconds
        
        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 40)

        # Collision boxes (hallway boundaries and doors)
        self.collision_boxes = [
            pygame.Rect(-1, 0, 1, 720),  # Left of screen
            pygame.Rect(0, -1, 1280, 1),  # Top of screen
            pygame.Rect(1280, 0, 1, 720),  # Right of screen
            pygame.Rect(0, 720, 1280, 1),  # Bottom of screen

            # Back wall Left
            pygame.Rect(0, 0, 395, 320),

            # Back wall right
            pygame.Rect(636, 0, 644, 320),

            # Barrier (gets removed later)
            pygame.Rect(530, 0, 100, 720)
        ]
        
        # Load sprites
        andrew_original = pygame.image.load("assets/andrew.png").convert_alpha()
        andrew_width, andrew_height = andrew_original.get_size()
        andrew_scale = 60 / andrew_height
        self.andrew_sprite = pygame.transform.scale(andrew_original, (int(andrew_width * andrew_scale)/60 * 100, 100))
        
        hall_monitor_original = pygame.image.load("assets/hall_monitor.png").convert_alpha()
        monitor_width, monitor_height = hall_monitor_original.get_size()
        monitor_scale = 60 / monitor_height
        self.hall_monitor_sprite = pygame.transform.scale(hall_monitor_original, (int(monitor_width * monitor_scale)/60 * 100, 100))
        
        principal_son_original = pygame.image.load("assets/principals_son.png").convert_alpha()
        son_width, son_height = principal_son_original.get_size()
        son_scale = 60 / son_height
        self.principal_son_sprite = pygame.transform.scale(principal_son_original, (int(son_width * son_scale)/60 * 100, 100))
        
        # Hall monitor position (blocks the way)
        self.hall_monitor_pos = pygame.math.Vector2(500, 360)
        self.hall_monitor_paid = False
        self.barrier_removed = False
        self.interaction_radius = 60
        
        # Store position (at the end of hallway)
        self.store_pos = pygame.math.Vector2(1100, 360)
        self.in_store = False
        
        # Store items and prices
        self.store_items = {
            "Bicycle": {"price": 50, "purchased": False},
            "Costco Membership": {"price": 100, "purchased": False},
            "Candy Machine": {"price": 200, "purchased": False},
            "Bigger Backpack": {"price": 75, "purchased": False}
        }
    
    def process_input(self, events):
        super().process_input(events)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:

                    # Interact with hall monitor or store
                    
                    if not self.hall_monitor_paid:
                        # Check if near hall monitor
                        distance = (self.player_pos - self.hall_monitor_pos).length()
                        if distance < self.interaction_radius:
                            # Try to pay with any candy
                            self._pay_hall_monitor()
                    else:
                        # Check if near store
                        distance = (self.player_pos - self.store_pos).length()
                        if distance < self.interaction_radius:
                            self.in_store = not self.in_store
                
                # Store navigation
                if self.in_store:
                    if event.key == pygame.K_1:
                        self._buy_item("Bicycle")
                    elif event.key == pygame.K_2:
                        self._buy_item("Costco Membership")
                    elif event.key == pygame.K_3:
                        self._buy_item("Candy Machine")
                    elif event.key == pygame.K_4:
                        self._buy_item("Bigger Backpack")
                    elif event.key == pygame.K_ESCAPE:
                        self.in_store = False
    
    def update(self, dt):
        super().update(dt)
        
        # Remove barrier if applicable
        if self.hall_monitor_paid and not self.barrier_removed:
            self.collision_boxes.pop()
            self.barrier_removed = True
        
        # Move player
        super().move(dt)
    
    def render(self, screen):
        super().render(screen, "Hallway")

        self.draw_characters(screen)
        self.draw_hall_monitor_interaction_hint(screen)
        self.draw_store_interaction_hint(screen)
        self.draw_barrier(screen)
        self.draw_store_UI(screen)
        
        self.draw_clock(screen)
        self.draw_inventory(screen)

    def draw_characters(self, screen):
        # Draw player (Andrew)
        andrew_rect = self.andrew_sprite.get_rect(center=self.player_pos)
        screen.blit(self.andrew_sprite, andrew_rect)

        # Draw hall monitor
        monitor_rect = self.hall_monitor_sprite.get_rect(center=self.hall_monitor_pos)
        screen.blit(self.hall_monitor_sprite, monitor_rect)

        # Draw principal's son (store)
        son_rect = self.principal_son_sprite.get_rect(center=self.store_pos)
        screen.blit(self.principal_son_sprite, son_rect)

    def draw_hall_monitor_interaction_hint(self, screen):
        # Draw interaction hint for hall monitor
        if not self.hall_monitor_paid:
            distance = (self.player_pos - self.hall_monitor_pos).length()
            if distance < self.interaction_radius:
                hint_text = "Press E - Pay 1 candy to pass"
                hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                hint_rect = hint_surface.get_rect(center=(self.hall_monitor_pos.x, self.hall_monitor_pos.y - 50))
                screen.blit(hint_surface, hint_rect)
                
                # Show dialogue
                dialogue = '"You gotta pay the candy toll, buddy."'
                dialogue_surface = self.small_font.render(dialogue, True, (255, 255, 255))
                dialogue_rect = dialogue_surface.get_rect(center=(self.hall_monitor_pos.x, self.hall_monitor_pos.y - 80))
                screen.blit(dialogue_surface, dialogue_rect)
        else:
            # Hall monitor looks away
            away_text = self.small_font.render("(Looking away)", True, (150, 150, 150))
            away_rect = away_text.get_rect(center=(self.hall_monitor_pos.x, self.hall_monitor_pos.y - 50))
            screen.blit(away_text, away_rect)

    def draw_store_interaction_hint(self, screen):
        # Draw store interaction hint
        if self.hall_monitor_paid:
            distance = (self.player_pos - self.store_pos).length()
            if distance < self.interaction_radius and not self.in_store:
                hint_text = "Press E - Visit Store"
                hint_surface = self.font.render(hint_text, True, (255, 255, 0))
                hint_rect = hint_surface.get_rect(center=(self.store_pos.x, self.store_pos.y - 50))
                screen.blit(hint_surface, hint_rect)

    def draw_barrier(self, screen):
        # Draw physical barrier if not paid (full width)
        if not self.hall_monitor_paid:
            # Draw a visible barrier/block spanning full hallway width
            barrier_width = 100  # Full screen width
            barrier_height = 700
            barrier_rect = pygame.Rect(
                self.hall_monitor_pos.x + 30,  # Start from left edge
                self.hall_monitor_pos.y - barrier_height // 2,
                barrier_width,
                barrier_height
            )
            # Draw barrier with red color to indicate it's blocking
            barrier_surface = pygame.Surface((barrier_width, barrier_height), pygame.SRCALPHA)
            barrier_surface.fill((255, 0, 0, 150))  # Semi-transparent red
            screen.blit(barrier_surface, barrier_rect)
            pygame.draw.rect(screen, (255, 0, 0), barrier_rect, 3)
            
            # Draw "BLOCKED" text on barrier
            blocked_text = self.font.render("BLOCKED - Pay toll to pass", True, (255, 255, 255))
            blocked_rect = blocked_text.get_rect(center=barrier_rect.center)
            screen.blit(blocked_text, blocked_rect)

    def draw_store_UI(self, screen):
        # Draw store UI
        if self.in_store:
            # Dim background
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Store box
            box_w, box_h = 600, 500
            box_x = (screen.get_width() - box_w) // 2
            box_y = (screen.get_height() - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(screen, (50, 50, 50), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 3)
            
            # Store title
            title_text = self.title_font.render("Principal's Son's Store", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(box_x + box_w // 2, box_y + 30))
            screen.blit(title_text, title_rect)
            
            # Store items
            y_offset = box_y + 80
            item_num = 1
            for item_name, item_data in self.store_items.items():
                # Item name and price
                purchased_text = " [PURCHASED]" if item_data["purchased"] else ""
                item_text = f"{item_num}. {item_name} - ${item_data['price']}{purchased_text}"
                item_color = (150, 150, 150) if item_data["purchased"] else (255, 255, 255)
                item_surface = self.font.render(item_text, True, item_color)
                screen.blit(item_surface, (box_x + 30, y_offset))
                
                # Item description
                descriptions = {
                    "Bicycle": "Helps your brother use less time traveling",
                    "Costco Membership": "Bulk candy deals (PS5 can be bought here)",
                    "Candy Machine": "Generates 10 free candy/day",
                    "Bigger Backpack": "Carry more items"
                }
                desc_text = descriptions.get(item_name, "")
                desc_surface = self.small_font.render(desc_text, True, (200, 200, 200))
                screen.blit(desc_surface, (box_x + 50, y_offset + 30))
                
                y_offset += 80
                item_num += 1
            
            # Instructions
            inst_text = "Press 1-4 to buy, ESC to close"
            inst_surface = self.small_font.render(inst_text, True, (255, 255, 0))
            inst_rect = inst_surface.get_rect(center=(box_x + box_w // 2, box_y + box_h - 30))
            screen.blit(inst_surface, inst_rect)

    def _pay_hall_monitor(self):
        """Pay the hall monitor with 1 piece of any candy"""
        candy = self.save["candy"]
        
        # Check for any candy type
        paid = False
        if candy.get("twizzlers", 0) > 0:
            candy["twizzlers"] -= 1
            paid = True
        elif candy.get("Skizzles", 0) > 0:
            candy["Skizzles"] -= 1
            paid = True
        elif candy.get("woozers", 0) > 0:
            candy["woozers"] -= 1
            paid = True
        
        if paid:
            self.hall_monitor_paid = True
            self.save_game()
    
    def _buy_item(self, item_name):
        """Buy an item from the store"""
        if item_name in self.store_items:
            item = self.store_items[item_name]
            if not item["purchased"] and self.save["money"] >= item["price"]:
                self.save["money"] -= item["price"]
                item["purchased"] = True
                
                # Apply item effects and track purchased items
                if item_name == "Bicycle":
                    self.save["bB_speed"] = 600.0  # Faster movement for brother
                    self.save["has_bicycle"] = True
                elif item_name == "Costco Membership":
                    self.save["has_costco_membership"] = True
                elif item_name == "Candy Machine":
                    self.save["has_candy_machine"] = True
                    # Will generate 10 candy per day (handled elsewhere)
                elif item_name == "Bigger Backpack":
                    self.save["has_bigger_backpack"] = True
                    # Increase inventory capacity (handled elsewhere)
                
                self.save_game()