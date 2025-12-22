import json
import os

SETTINGS_FILE = 'settings.json'

class Settings:
    def __init__(self):
        self.data = {
            "last_folder": None
        }
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    self.data = json.load(f)
            except:
                pass # Ignore errors, stick to defaults

    def save(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.data, f)

    def get_last_folder(self):
        return self.data.get("last_folder")

    def set_last_folder(self, path):
        self.data["last_folder"] = path
        self.save()
