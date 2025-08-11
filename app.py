import sys
import os
import signal
import sys

# allows graceful shutdown on SIGINT (Ctrl+C) or SIGTERM
def signal_handler(sig, frame):
    print('\nReceived interrupt signal, exiting gracefully...')
    sys.exit(0)

# Add this at the start of your main.py
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

current_dir = os.getcwd()

# Add current directory to Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.example import main # change this to your own module. make sure the file is in the src directory.
except ImportError as e:
    print(f"Import error: {e}")
    # List all Python files for debugging
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"Python files in directory: {py_files}")
    raise

if __name__ == "__main__":
    result = main()
    sys.exit(result if result is not None else 0)
