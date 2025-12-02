import pygame
import os
from .scene_template import Scene
from .ui_button import Button
from save_manager import load_save, save_data, DEFAULT_DATA

# this was pretty complicated so we used AI a good portion for this

SAVE_DIR = "saves/"

class load_save_menu(Scene):
    def __init__(self):
        super().__init__(None, "title_screen", "title_bg.png") 

        self.title_font = pygame.font.Font(None, 80)
        self.button_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30) # using small_font from base scene class

        self.buttons = []
        self.save_files = self.get_save_files()
        self.make_buttons()
        
        self.destination_scene = "brother_a_transition" 

    def process_input(self, events):
        mouse_pos = pygame.mouse.get_pos()

        for e in events:
            # handle esc to go back to the title screen
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.switch_to("title_screen")
                return

            # button Clicks
            for btn in self.buttons:
                if btn.clicked(mouse_pos, e):
                    
                    if btn == self.back_btn:
                        self.switch_to("title_screen")
                        
                    elif btn == self.new_game_btn:
                        #sse load save to set the global save path in save_manager.py
                        print(f"Creating/Resetting New Game: {btn.filename}")
                        load_save(btn.filename)
                        
                        # save the default data to the file path
                        save_data(DEFAULT_DATA.copy())
                        
                        #switch to the game start scene
                        self.switch_to(self.destination_scene)

                    elif hasattr(btn, 'filename'):
                        #this is an existing save file button
                        print(f"Loading save file: {btn.filename}")
                        
                        #load the selected save file
                        load_save(btn.filename) 
                        
                        #switch to the game start scene
                        self.switch_to(self.destination_scene)


    def update(self, dt):
        # only update the buttons for hover effects
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, screen):
        super().render(screen, tool_tips=False)

        # title text
        title_surf = self.title_font.render("SUGAR RUSH - LOAD GAME", True, (255, 215, 0))
        rect = title_surf.get_rect(center=(screen.get_width() // 2, 80))
        
        # simple drop shadow for visibility
        screen.blit(self.title_font.render("SUGAR RUSH - LOAD GAME", True, (0, 0, 0)), (rect.x + 4, rect.y + 4))
        screen.blit(title_surf, rect)

        # draw buttons
        for btn in self.buttons:
            btn.draw(screen)
            
    def get_save_files(self):
        """Scans the 'saves' directory and returns a list of filenames without the '.json' extension."""
        files = [f.replace(".json", "") for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        return sorted(files)

    def _get_next_save_filename(self):
        """Determines the next sequential save file name (e.g., 'save_data3')."""
        max_num = 0
        for filename in self.save_files:
            # check if filename matches 'save_dataX' pattern
            # starts with 'save_data' (9 chars) and the rest are digits
            if filename.startswith("save_data") and filename[9:].isdigit():
                try:
                    # Extract the number part
                    num = int(filename[9:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        
        # the next number is one higher than the maximum found
        next_num = max_num + 1
        return f"save_data{next_num}"

    def make_buttons(self):
        """Creates buttons for each existing save file, plus 'New Game' and 'Back'."""
        screen_w, screen_h = 1280, 720 # reference screen size for positioning
        cx = screen_w // 2
        
        # start vertical position for the first button 
        y_start = 180
        spacing = 65
        
        # new game button ####
        next_save_name = self._get_next_save_filename()
        new_game_text = f"START NEW GAME (Save to {next_save_name})"
        
        self.new_game_btn = Button(new_game_text, (cx, y_start), self.button_font, (50, 255, 50), (0, 150, 0))
        # use the determined  name
        self.new_game_btn.filename = next_save_name 
        self.buttons.append(self.new_game_btn)
        y_start += spacing + 10 # a lil extra space


        # saves
        for i, filename in enumerate(self.save_files):
            y_pos = y_start + (i * spacing)
            
            # load the data briefly to display a summary
            try:
                # use load save function to read the file content
                data_preview = load_save(filename)
                money = data_preview.get("money", 0)
                buyers = data_preview.get("buyers", 0)
                
                button_text = f"{filename} - Cash: ${money} / Buyers: {buyers}"
            except Exception:
                button_text = f"{filename} - (Corrupt Data)"
                
            btn = Button(button_text, (cx, y_pos), self.small_font, (255, 255, 255), (150, 150, 255))
            
            # store the filename on the button object for easy retrieval during click
            btn.filename = filename 
            self.buttons.append(btn)


        # back button
        y_back = screen_h - 80
        self.back_btn = Button("BACK TO TITLE", (cx, y_back), self.button_font, (255, 255, 255), (255, 100, 100))
        self.buttons.append(self.back_btn)
