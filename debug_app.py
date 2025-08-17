#!/usr/bin/env python3
"""
Debug wrapper for app.py that enables remote debugging when run inside gnubg.
Usage: gnubg -t -p debug_app.py
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def setup_remote_debugging():
    """Setup remote debugging if debugpy is available"""
    try:
        import debugpy
        
        # Enable debugging on port 5678
        debugpy.listen(("localhost", 5678))
        print("Debug server started on localhost:5678")
        print("Attach VSCode debugger using 'GNU Backgammon: Remote Debug' configuration")
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("Debugger attached!")
        
    except ImportError:
        print("debugpy not installed. Install with: pip install debugpy")
        print("Running without remote debugging...")
    except Exception as e:
        print(f"Failed to setup debugging: {e}")
        print("Running without remote debugging...")

if __name__ == "__main__":
    # Setup remote debugging
    setup_remote_debugging()
    
    # Import and run the main app
    try:
        import app
        # If app has a main function, call it
        if hasattr(app, 'main'):
            app.main()
        elif hasattr(app, 'run'):
            app.run()
    except ImportError:
        print("Could not import app.py")
        sys.exit(1)