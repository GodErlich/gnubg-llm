import sys
import time
import os
import threading
import json
import re

class Logger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, log_file: str = "game", output_folder: str = "output", debug_mode: bool = False):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Logger, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_file: str = "game", output_folder: str = "output", debug_mode: bool = False, json_format: bool = False):
        if not self._initialized:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            log_file_name = f"{log_file}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            self.log_file = os.path.join(output_folder, log_file_name)
            self.debug_mode = debug_mode
            self.json_format = json_format
            self._initialized = True
    
    def log(self, level: str, message: str):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        if self.json_format:
            # Use JSON format for structured logging
            log_data = {
                "timestamp": timestamp,
                "level": level,
                "message": message
            }
            log_entry = json.dumps(log_data, ensure_ascii=False) + "\n"
        else:
            # Handle multi-line messages by converting to single line
            clean_message = self._clean_message(message)
            log_entry = f"[{timestamp}] - {level}: {clean_message}\n"
        
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(log_entry)
    
    def _clean_message(self, message: str) -> str:
        """Clean message for single-line logging by replacing newlines and excessive whitespace."""
        if not message:
            return ""
        
        # Replace newlines with literal \n
        clean = message.replace('\n', '\\n').replace('\r', '\\r')
        
        # Replace multiple spaces/tabs with single space
        clean = re.sub(r'\s+', ' ', clean)
        
        # Trim whitespace
        clean = clean.strip()
        
        return clean
    
    def debug(self, message: str):
        if self.debug_mode:
            self.log("DEBUG", message)
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
        # Also print to stderr for immediate visibility
        clean_message = self._clean_message(message)
        print(f"ERROR: {clean_message}", file=sys.stderr)

    def warning(self, message: str):
        self.log("WARNING", message)
    
    def set_debug_mode(self, debug_mode: bool):
        """Update the debug mode after initialization."""
        self.debug_mode = debug_mode
    
    def set_json_format(self, json_format: bool):
        """Update the JSON format mode after initialization."""
        self.json_format = json_format
    
    def log_multiline(self, level: str, message: str, preserve_formatting: bool = False):
        """Log a multi-line message with option to preserve formatting."""
        if preserve_formatting and self.json_format:
            # In JSON mode, preserve the original formatting
            self.log(level, message)
        elif preserve_formatting:
            # In text mode with formatting preserved, log each line separately
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            lines = message.split('\n')
            with open(self.log_file, "a", encoding='utf-8') as f:
                for i, line in enumerate(lines):
                    if i == 0:
                        f.write(f"[{timestamp}] - {level}: {line}\n")
                    else:
                        f.write(f"[{timestamp}] - {level}_CONT: {line}\n")
        else:
            # Use the standard cleaning approach
            self.log(level, message)

# Global logger instance
logger = Logger()
