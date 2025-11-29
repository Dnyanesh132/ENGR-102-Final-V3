import json
import os

SAVE_PATH = "saves/save_data1.json"

# This works like a dictionary in other files
DEFAULT_DATA = {
    "buyers": 0,
    "money": 0,
    "candy":{
        "twizzlers": 15,
        "Skizzles": 0,
        "woozers": 0    
    },
    "bA_speed": 400.0,
    "bB_speed": 400.0,
    "has_costco_membership": False,
    "settings": {
        "fullscreen": False,
        "audio": 100,
    }
}

def load_save(save_file = None):
    """Load game data from JSON. If not found, create default."""
    # Choose a different save file
    global SAVE_PATH
    if save_file is not None:
        SAVE_PATH = f"saves/{save_file}.json"
        
    if not os.path.exists(SAVE_PATH):
        save_data(DEFAULT_DATA)  # create a new save file
        return DEFAULT_DATA.copy()

    with open(SAVE_PATH, "r") as f:
        data = json.load(f)
    return data

def save_data(data):
    """Write the data dictionary to the JSON file."""
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=4)
