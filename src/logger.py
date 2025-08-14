import time
import os
import threading

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
    
    def __init__(self, log_file: str = "game", output_folder: str = "output", debug_mode: bool = False):
        if not self._initialized:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            log_file_name = f"{log_file}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            self.log_file = os.path.join(output_folder, log_file_name)
            self.debug_mode = debug_mode
            self._initialized = True
    
    def log(self, message: str):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] - {message}\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        
        if self.debug_mode:
            print(f"[{timestamp}] - {message}")
    
    def debug(self, message: str):
        if self.debug_mode:
            self.log(f"DEBUG: {message}")
    
    def info(self, message: str):
        self.log(f"INFO: {message}")
    
    def error(self, message: str):
        self.log(f"ERROR: {message}")
    
    def warning(self, message: str):
        self.log(f"WARNING: {message}")
    
    def set_debug_mode(self, debug_mode: bool):
        """Update the debug mode after initialization."""
        self.debug_mode = debug_mode

# Global logger instance
logger = Logger()
