#!/usr/bin/env python3
"""
Debug script to check git repository status and help diagnose commit issues.
"""
import os
import sys
from pathlib import Path

from core.config import Config

# Add application directory to Python path
repo_root = Config.get_base_path()
app_dir = repo_root / "application"
sys.path.insert(0, str(app_dir))

from utils.git import GitHelper
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def main():
    print("=== Git Repository Status Debug ===\n")
    
    try:
        with GitHelper() as helper:
            print(f"Repository path: {helper.get_repo_root()}")
            print(f"Current branch: {helper.get_current_branch()}")
            print()
            
            # Check for changes
            unstaged, staged = helper.has_changes()
            print(f"Has unstaged changes: {unstaged}")
            print(f"Has staged changes: {staged}")
            print()
            
            # Get detailed status
            status = helper.get_status()
            print("=== File Status ===")
            for category, files in status.items():
                if files:
                    print(f"{category.title()}: {len(files)} files")
                    for file in files[:5]:  # Show first 5 files
                        print(f"  - {file}")
                    if len(files) > 5:
                        print(f"  ... and {len(files) - 5} more")
                else:
                    print(f"{category.title()}: 0 files")
            print()
            
            # Get detailed status string
            success, status_msg = helper.get_status_detailed()
            print("=== Detailed Status ===")
            print(status_msg)
            print()
            
            # Check remotes
            remotes = helper.get_remotes()
            print(f"Remotes: {remotes}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
