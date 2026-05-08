#!/usr/bin/env python3
"""
Test script to verify the base path configuration.
"""
import sys
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from core.config import Config
from core.analyzer.markdown_analyzer import MarkdownAnalyzer

def test_paths():
    """Test the base path configuration."""
    print("Testing base path configuration...")
    
    # Test Config base path
    config_base_path = Config.get_base_path()
    print(f"Config base path: {config_base_path}")
    print(f"Config base path exists: {config_base_path.exists()}")
    print(f"Config base path absolute: {config_base_path.resolve()}")
    
    # Test default markdown path
    default_md_path = Config.get_default_markdown_path()
    print(f"Default markdown path: {default_md_path}")
    print(f"Default markdown exists: {Path(default_md_path).exists()}")
    
    # Test MarkdownAnalyzer base path
    analyzer = MarkdownAnalyzer()
    print(f"Analyzer base path: {analyzer.base_path}")
    print(f"Analyzer base path exists: {analyzer.base_path.exists()}")
    print(f"Analyzer base path absolute: {analyzer.base_path.resolve()}")
    
    # Test if they're the same
    print(f"Paths are equal: {config_base_path.resolve() == analyzer.base_path.resolve()}")
    
    # List contents of base path
    print(f"\nContents of base path:")
    if analyzer.base_path.exists():
        for item in analyzer.base_path.iterdir():
            print(f"  - {item.name}")

if __name__ == "__main__":
    test_paths()
