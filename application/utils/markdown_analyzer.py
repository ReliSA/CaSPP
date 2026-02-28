import re
import os
from pathlib import Path
from typing import List, Dict, Tuple

class MarkdownAnalyzer:
    def __init__(self, base_path: str = None):
        """
        Initialize the analyzer.
        
        Args:
            base_path: Base path for the project (mainly used for file dialogs and default locations)
        """
        if base_path is None:
            # Default to the project root (parent of application directory)
            app_dir = Path(__file__).parent.parent
            self.base_path = app_dir.parent
        else:
            self.base_path = Path(base_path)
    
    def find_markdown_links(self, content: str) -> List[Dict[str, str]]:
        """
        Find all markdown links in the content.
        Returns a list of dictionaries with 'text', 'url', and 'type' keys.
        """
        links = []
        
        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            
            # Determine if it's a markdown file link
            link_type = "markdown" if url.endswith('.md') else "other"
            
            links.append({
                'text': text,
                'url': url,
                'type': link_type,
                'line_position': content[:match.start()].count('\n') + 1
            })
        
        return links
    
    def check_file_exists(self, file_path: str, relative_to_file: str) -> Tuple[bool, str]:
        """
        Check if a file exists relative to the analyzed file's location.
        Returns (exists, absolute_path)
        
        Args:
            file_path: The file path to check (from markdown link)
            relative_to_file: The path of the markdown file being analyzed
        """
        # Get the directory of the analyzed file
        analyzed_file_dir = Path(relative_to_file).parent
        
        # Handle relative paths
        if not os.path.isabs(file_path):
            full_path = analyzed_file_dir / file_path
        else:
            full_path = Path(file_path)
        
        return full_path.exists(), str(full_path.resolve())
    
    def analyze_markdown_file(self, file_path: str) -> Dict:
        """
        Analyze a markdown file for structure and linked files.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            return {'error': f'File not found: {file_path}'}
        
        # Find all links
        links = self.find_markdown_links(content)
        
        # Check which markdown links exist
        markdown_links = [link for link in links if link['type'] == 'markdown']
        
        link_status = []
        for link in markdown_links:
            exists, full_path = self.check_file_exists(link['url'], file_path)
            link_status.append({
                'text': link['text'],
                'url': link['url'],
                'exists': exists,
                'full_path': full_path,
                'line': link['line_position']
            })
        
        # Extract headings for structure
        headings = self.extract_headings(content)
        
        return {
            'file_path': file_path,
            'total_links': len(links),
            'markdown_links': len(markdown_links),
            'other_links': len(links) - len(markdown_links),
            'link_status': link_status,
            'headings': headings,
            'missing_files': [link for link in link_status if not link['exists']],
            'existing_files': [link for link in link_status if link['exists']]
        }
    
    def extract_headings(self, content: str) -> List[Dict[str, str]]:
        """Extract all headings from markdown content."""
        headings = []
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2)
                headings.append({
                    'level': level,
                    'text': text,
                    'line': line_num
                })
        
        return headings
    
    def generate_report(self, analysis: Dict) -> str:
        """Generate a human-readable report of the analysis."""
        if 'error' in analysis:
            return f"Error: {analysis['error']}"
        
        report = f"# Markdown Analysis Report\n\n"
        report += f"**File:** {analysis['file_path']}\n\n"
        
        # Structure overview
        report += f"## Structure Overview\n"
        report += f"- Total links found: {analysis['total_links']}\n"
        report += f"- Markdown file links: {analysis['markdown_links']}\n"
        report += f"- Other links: {analysis['other_links']}\n\n"
        
        # Headings
        if analysis['headings']:
            report += f"## Document Structure\n"
            for heading in analysis['headings']:
                indent = "  " * (heading['level'] - 1)
                report += f"{indent}- {heading['text']} (Line {heading['line']})\n"
            report += "\n"
        
        # Missing files
        if analysis['missing_files']:
            report += f"## ❌ Missing Linked Files\n"
            for link in analysis['missing_files']:
                report += f"- **{link['text']}** → `{link['url']}` (Line {link['line']})\n"
            report += "\n"
        
        # Existing files
        if analysis['existing_files']:
            report += f"## ✅ Existing Linked Files\n"
            for link in analysis['existing_files']:
                report += f"- **{link['text']}** → `{link['url']}` (Line {link['line']})\n"
            report += "\n"
        
        return report
    
    def get_base_path(self) -> Path:
        """Get the base path for file operations (e.g., file dialogs)."""
        return self.base_path
