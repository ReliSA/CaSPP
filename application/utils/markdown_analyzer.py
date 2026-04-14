import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
import logging

from core.constants import FileConstants
from utils.exceptions import FileNotFoundError, FileReadError, InvalidInputError
from utils.markdown_parser import ParsedDocument
from utils.template_parser import TemplateRules

logger = logging.getLogger(__name__)

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
            # Validate base_path
            if not isinstance(base_path, (str, Path)):
                raise InvalidInputError("base_path", base_path, "must be a string or Path object")
            
            base_path_obj = Path(base_path)
            if not base_path_obj.exists():
                raise FileNotFoundError(str(base_path_obj))
                
            self.base_path = base_path_obj

        self.current_errors = []
        self.current_warnings = []
    
    def find_markdown_links(self, content: str) -> List[Dict[str, str]]:
        """
        Find all markdown links in the content.
        Returns a list of dictionaries with 'text', 'url', and 'type' keys.
        """
        if not isinstance(content, str):
            raise InvalidInputError("content", content, "must be a string")
        
        if not content.strip():
            return []
        
        links = []
        
        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            
            # Determine if it's a markdown file link
            link_type = "markdown" if any(url.endswith(ext) for ext in FileConstants.MARKDOWN_EXTENSIONS) else "other"
            
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
        # Input validation
        if not isinstance(file_path, str) or not file_path.strip():
            raise InvalidInputError("file_path", file_path, "must be a non-empty string")
        
        if not isinstance(relative_to_file, str) or not relative_to_file.strip():
            raise InvalidInputError("relative_to_file", relative_to_file, "must be a non-empty string")
        
        try:
            # Get the directory of the analyzed file
            analyzed_file_dir = Path(relative_to_file).parent
            
            # Handle relative paths
            if not os.path.isabs(file_path):
                full_path = analyzed_file_dir / file_path
            else:
                full_path = Path(file_path)
            
            return full_path.exists(), str(full_path.resolve())
            
        except (OSError, ValueError) as e:
            logger.warning(f"Error checking file existence for '{file_path}': {e}")
            return False, ""
    
    def analyze_markdown_file(self, file_path: str, template_rules=None) -> Dict:
        """
        Analyze a markdown file for structure and linked files.
        """
        # Input validation
        if not isinstance(file_path, str) or not file_path.strip():
            raise InvalidInputError("file_path", file_path, "must be a non-empty string")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(str(file_path_obj))
            
        # Check if it's a markdown file
        if not any(file_path.lower().endswith(ext) for ext in FileConstants.MARKDOWN_EXTENSIONS):
            logger.warning(f"File '{file_path}' is not a markdown file")
        
        try:
            with open(file_path, 'r', encoding=FileConstants.ENCODING_UTF8, errors="replace") as file:
                content = file.read()
                
        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read file '{file_path}': {e}")
            raise FileReadError(file_path, str(e)) from e
        
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
            'existing_files': [link for link in link_status if link['exists']],
        }
    
    def extract_headings(self, content: str) -> List[Dict[str, str]]:
        """Extract all headings from markdown content."""
        if not isinstance(content, str):
            raise InvalidInputError("content", content, "must be a string")
        
        if not content.strip():
            return []
            
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
        if not isinstance(analysis, dict):
            raise InvalidInputError("analysis", analysis, "must be a dictionary")
        
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

        if 'structure_results' in analysis:
            res = analysis['structure_results']
            report += "##  Structural Validation\n"
            
            if not res['errors'] and not res['warnings']:
                report += "✅ Structure is alright according to template.\n"
            else:
                for err in res['errors']:
                    report += f"- ❌ **Line {err['line']}:** {err['msg']}\n"
                for warn in res['warnings']:
                    report += f"- ⚠️ **Line {warn['line']}:** {warn['msg']}\n"
            report += "\n"
        
        return report
    
    def get_base_path(self) -> Path:
        """Get the base path for file operations (e.g., file dialogs)."""
        return self.base_path  
    
    def validate_structure(self, doc: 'ParsedDocument', template: 'TemplateRules') -> Dict:
        """Compares the parsed document against template rules.

        This method performs a structural validation of the markdown file, 
        checking for mandatory headings, correct heading levels, and 
        validating content within individual sections.

        Args:
            doc (ParsedDocument): The parsed representation of the markdown 
                file containing metadata and headings.
            template (TemplateRules): The set of rules and expectations 
                defined in the matching template.

        Returns:
            Dict[str, Any]: A dictionary containing the validation results:
                - 'file': Absolute path to the analyzed file.
                - 'errors': List of dictionaries with 'line' and 'msg' keys 
                  representing critical rule violations.
                - 'warnings': List of dictionaries representing non-critical 
                  issues (e.g., missing optional sections).
        """
        print(f"DEBUG: Validuji soubor {doc.meta.filepath} proti šabloně.")

        self.current_errors = []
        self.current_warnings = []
        
        self.validate_breadcrumbs(doc.meta, template.document_rules)
        
        doc_h1 = next((h for h in doc.headings if h.level == 1), None)
        if not doc_h1:
            self._add_error(1, "V souboru chybí hlavní nadpis (H1)")
        
        doc_headings_map = {h.text: h for h in doc.headings}
        
        for t_heading in template.headings:
            if t_heading.level == 1 and t_heading.is_variable:
                if doc_h1:
                    self.check_content(doc_h1.content, t_heading.content_rules, doc_h1.line_number)
                continue

            actual = doc_headings_map.get(t_heading.text)
            
            if not actual:
                if not t_heading.optional:
                    self.current_errors.append({"line": 0, "msg": f"Chybí povinný nadpis: {t_heading.text}"})
            else:
                if actual.level != t_heading.level:
                    self.current_errors.append({
                        "line": actual.line_number, 
                        "msg": f"Nadpis '{actual.text}' má úroveň H{actual.level}, ale šablona vyžaduje H{t_heading.level}"
                    })
                
                self.check_content(actual.content, t_heading.content_rules, actual.line_number)

        return {
            "file": doc.meta.filepath,
            "errors": self.current_errors,
            "warnings": self.current_warnings
        }

    def check_content(self, actual_content, rules, line_num):
        """Kontrola typů obsahu a tabulek uvnitř sekce."""
        # Kontrola tabulek
        if rules.table_headers:
            if not actual_content.table_headers:
                self.current_errors.append({"line": line_num, "msg": "V této sekci chybí povinná tabulka"})
            elif actual_content.table_headers != rules.table_headers:
                self.current_errors.append({
                    "line": line_num, 
                    "msg": f"Tabulka má špatné sloupce. Očekáváno: {rules.table_headers}"
                })
        
        # Kontrola povinných prefixů
        for pref in rules.exact_list_prefixes:
            if pref not in actual_content.exact_list_prefixes:
                self.current_errors.append({"line": line_num, "msg": f"V seznamu chybí povinná položka: {pref}"})

    def validate_breadcrumbs(self, doc_meta, doc_rules):
        """Validates the breadcrumb navigation line at the top of the document.

        Checks the breadcrumbs against the template rules (items 9, 10 and 11 in the excel table).

        Args:
            doc_meta (Any): Metadata object from the parsed document containing 
                'breadcrumbs' (list of strings) and 'filepath' (str).
            doc_rules (Any): Rule object from the template containing 
                'breadcrumbs' (list of expected strings/placeholders).

        Returns:
            None: The method updates the internal state of current_errors/warnings.
        """
        # 9. Přítomnost breadcrumbs
        if not doc_meta.breadcrumbs:
            self._add_error(1, "Dokument neobsahuje breadcrumbs.")
            return

        temp_crumbs = doc_rules.breadcrumbs
        actual_crumbs = doc_meta.breadcrumbs

        # 10. Počet částí
        if len(actual_crumbs) != len(temp_crumbs):
            self._add_error(1, f"Breadcrumbs mají špatný počet částí. Očekáváno {len(temp_crumbs)}, nalezeno {len(actual_crumbs)}.")
            return

        # 11. Obsah částí
        for i, (t_part, a_part) in enumerate(zip(temp_crumbs, actual_crumbs)):
            if t_part.startswith("*") and t_part.endswith("*"):
                if not a_part.strip():
                    self._add_error(1, f"Část breadcrumbs '{t_part}' (proměnná) nesmí být prázdná.")
                continue

            if t_part != a_part:
                self._add_error(1, f"Breadcrumb část č. {i+1} neodpovídá šabloně. Očekáváno: '{t_part}', nalezeno: '{a_part}'.")



    def _add_error(self, line: int, msg: str) -> None:
        """Adds a validation error.

        Args:
            line (int): The 1-based line number where the error occurred.
            msg (str): A description of the error.

        Returns:
            None
        """
        if not hasattr(self, 'current_errors'):
            self.current_errors = []
        self.current_errors.append({"line": line, "msg": msg})

    def _add_warning(self, line: int, msg: str) -> None:
        """Adds a validation warning to the current analysis session.

        Args:
            line (int): The 1-based line number where the issue was found.
            msg (str): A description of the potential problem.

        Returns:
            None
        """
        if not hasattr(self, 'current_warnings'):
            self.current_warnings = []
        self.current_warnings.append({"line": line, "msg": msg})
    