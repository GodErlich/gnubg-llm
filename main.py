import sys
import os

current_dir = os.getcwd()

# Add current directory to Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Also try /app directory explicitly
if '/app' not in sys.path:
    sys.path.insert(0, '/app')


try:
    from src.example import main # change this to your own module. make sure the file is in the src directory.
except ImportError as e:
    print(f"Import error: {e}")
    # List all Python files for debugging
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"Python files in directory: {py_files}")
    raise

if __name__ == "__main__":
    main()