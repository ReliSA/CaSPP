#!/usr/bin/env python3
"""
Test script to verify that file existence checking works relative to the analyzed file.
"""
import sys
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from utils.markdown_analyzer import MarkdownAnalyzer

def test_relative_path_checking():
    """Test the relative path checking functionality."""
    print("Testing relative path checking...")
    
    analyzer = MarkdownAnalyzer()
    
    # Test with a sample markdown file path
    sample_file = "/Users/trongquochuydinh/Documents/ASWI/STePSEnHECs-PaCt/README.md"
    
    # Test checking for various relative files
    test_cases = [
        "catalogue/2_2_makes_four_eyes.md",  # Should exist
        "application/main.py",  # Should exist
        "nonexistent.md",  # Should not exist
        "LICENSE",  # Should exist
    ]
    
    print(f"Testing from file: {sample_file}")
    print(f"File directory: {Path(sample_file).parent}")
    
    for test_path in test_cases:
        exists, full_path = analyzer.check_file_exists(test_path, sample_file)
        print(f"  {test_path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'} ({full_path})")

    # Test from a file in a subdirectory
    print(f"\n--- Testing from catalogue directory ---")
    catalogue_file = "/Users/trongquochuydinh/Documents/ASWI/STePSEnHECs-PaCt/catalogue/2_2_makes_four_eyes.md"
    
    test_cases_catalogue = [
        "../README.md",  # Should exist (parent directory)
        "A_Proper_Tool_Is_Half_The_Job_Done.md",  # Should exist (same directory)
        "../application/main.py",  # Should exist (relative to parent)
        "nonexistent.md",  # Should not exist
    ]
    
    print(f"Testing from file: {catalogue_file}")
    print(f"File directory: {Path(catalogue_file).parent}")
    
    for test_path in test_cases_catalogue:
        exists, full_path = analyzer.check_file_exists(test_path, catalogue_file)
        print(f"  {test_path}: {'✅ EXISTS' if exists else '❌ NOT FOUND'} ({full_path})")

if __name__ == "__main__":
    test_relative_path_checking()
