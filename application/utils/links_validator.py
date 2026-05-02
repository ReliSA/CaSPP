import os
import re
from typing import List, Dict, Any

from core.constants import LoaderConstants

class LinkValidator:
    """
    Validates markdown links and cross-references using the project index.

    This validator checks for broken links, missing reciprocal references between 
    design patterns, and ensures that link labels (aliases) match the metadata 
    defined in the target files.
    """

    def __init__(self, doc: Any, project_index: Dict[str, Any]):
        """
        Initializes the LinkValidator.

        Args:
            doc (ParsedDocument): The parsed representation of the current file.
            project_index (Dict[str, Any]): A global map containing metadata 
                (aliases, related links) for all files in the project.
        """
        self.doc = doc
        self.project_index = project_index
        full_name = os.path.basename(doc.meta.filepath)
        self.current_filename_stem = os.path.splitext(full_name)[0]
        self.current_filename_with_ext = full_name
        self.warnings = []

    def check_reciprocal_links(self) -> None:
        """
        Validates reciprocal links between patterns (Excel table 26 and 27).
        Ensures that if the current file links to another pattern in the 
        'Related Patterns' section, that target file also links back to the 
        current file. Also flags links to non-existent files.
        """
        current_file_key = self.current_filename_with_ext
        current_data = self.project_index.get(current_file_key)

        if not current_data:
            return

        for target_file_with_ext in current_data.get("related", []):
            target_clean = os.path.basename(target_file_with_ext)
            
            if target_clean in self.project_index:
                target_data = self.project_index[target_clean]
                target_related = [os.path.basename(r) for r in target_data.get("related", [])]

                if current_file_key not in target_related:
                    self.warnings.append({
                        "line": 1,
                        "msg": f"Reciprocal link missing. '{target_clean}' should link back to '{current_file_key}'."
                    })
            else:
                self.warnings.append({
                    "line": 1,
                    "msg": f"Linked file '{target_file_with_ext}' not found in project."
                })

    def check_alias_consistency(self) -> None:
        """
        Ensures link labels are recognized aliases of the target (Rule 28).
        """
        for heading in self.doc.headings:
            for line_entry in heading.content.raw_lines:
                line = line_entry["content"]
                links = LoaderConstants.RE_LINK_INTEGRITY.finditer(line)
                
                for match in links:
                    label = match.group(1)
                    url = match.group(2)

                    if not label or not url:
                        self.warnings.append({
                            "line": line_entry["line"],
                            "msg": f"Empty label or URL in link. Label: '[{label}]', URL: '({url})'."
                        })
                        continue
                    
                    raw_target = url.split('#')[0].replace('./', '').replace('../', '')
                    target_file_key = os.path.basename(raw_target)
                    
                    if not target_file_key.lower().endswith('.md'):
                        target_file_key += '.md'
                    
                    target_stem = os.path.splitext(target_file_key)[0]
                    
                    if target_file_key in self.project_index:
                        target_data = self.project_index[target_file_key]
                        target_aliases = target_data.get("aliases", [])
                        
                        if label != target_stem and label not in target_aliases:
                            self.warnings.append({
                                "line": line_entry["line"],
                                "msg": f"Link label '{label}' is not a recognized alias of '{target_file_key}'."
                            })


    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Runs all link-related validation rules.

        Returns:
            List[Dict[str, Any]]: A list of warning dictionaries, each containing 
                'line' and 'msg' keys.
        """
        self.warnings = []
        self.check_reciprocal_links()
        self.check_alias_consistency()
        return self.warnings