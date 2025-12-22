import re

class ConfigLine:
    TYPE_COMMENT = 'COMMENT'
    TYPE_KEY_VALUE = 'KEY_VALUE'
    TYPE_WHITESPACE = 'WHITESPACE'
    TYPE_UNKNOWN = 'UNKNOWN'

    def __init__(self, raw_line, line_num):
        self.raw_line = raw_line
        self.line_num = line_num
        self.type = self.determine_type(raw_line)
        self.key = None
        self.value = None
        self.comment = None
        
        if self.type == self.TYPE_KEY_VALUE:
            self.parse_key_value()
        elif self.type == self.TYPE_COMMENT:
            self.comment = raw_line.strip()

    def determine_type(self, line):
        stripped = line.strip()
        if not stripped:
            return self.TYPE_WHITESPACE
        if stripped.startswith('#'):
            return self.TYPE_COMMENT
        if '=' in stripped:
            # Check if it looks like a key=value pair
            # We assume keys don't start with # and exist before the first =
            parts = stripped.split('=', 1)
            if parts[0].strip():
                return self.TYPE_KEY_VALUE
        return self.TYPE_UNKNOWN

    def parse_key_value(self):
        parts = self.raw_line.split('=', 1)
        self.key = parts[0].strip()
        # Value might have an inline comment, though in these files comments seem to be mostly on separate lines
        # But let's check for "Key = Value # Comment" just in case, although strictly speaking 
        # in some INI formats # inside value is valid. 
        # Based on observed files, value is just the rest of the line.
        val_part = parts[1].strip()
        self.value = val_part
    
    def to_string(self):
        if self.type == self.TYPE_KEY_VALUE:
            # Reconstruct trying to preserve some original formatting if possible?
            # For now, standard "Key = Value" is likely fine, but let's try to match original indentation if we wanted to be perfect.
            # However, simpler is better for now.
            return f"{self.key} = {self.value}\n"
        else:
            return self.raw_line

class ConfigFile:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.lines = []
        self.key_map = {} # Maps key string to list of ConfigLine objects (indices or references)

    def load(self, filepath):
        self.filepath = filepath
        self.lines = []
        self.key_map = {}
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_lines = f.readlines()
            
        for i, raw in enumerate(raw_lines):
            line_obj = ConfigLine(raw, i)
            self.lines.append(line_obj)
            
            if line_obj.type == ConfigLine.TYPE_KEY_VALUE:
                self.key_map[line_obj.key] = line_obj

    def get_value(self, key):
        if key in self.key_map:
            return self.key_map[key].value
        return None

    def update_value(self, key, new_value):
        if key in self.key_map:
            line_obj = self.key_map[key]
            line_obj.value = new_value
            return True
        return False

    def save(self, filepath=None):
        target = filepath if filepath else self.filepath
        if not target:
            raise ValueError("No filepath specified for save")
            
        with open(target, 'w', encoding='utf-8') as f:
            for line in self.lines:
                f.write(line.to_string())
