import os
from typing import List, Dict, Any

from utils.constants import LoaderConstants

class LinkValidator:
    """
    Validates markdown links and cross-references using the project index.

    This validator checks for broken links, missing reciprocal references between 
    design patterns, and ensures that link labels (aliases) match the metadata 
    defined in the target files.
    """

    def __init__(self, doc: Any, project_index: Dict[str, Any], references_content: str = None):
        """
        Initializes the LinkValidator.

        Args:
            doc (ParsedDocument): The parsed representation of the current file.
            project_index (Dict[str, Any]): A global map containing metadata
                (aliases, related links) for all files in the project.
            references_content (str): Pre-read content of References.md, supplied by FileManager.
        """
        self.doc = doc
        self.project_index = project_index
        self.references_content = references_content
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

    def check_link_targets(self) -> None:
        """
        Validates that all relative markdown links point to files that exist
        in the project index.
        """
        for heading in self.doc.headings:
            for line_entry in heading.content.raw_lines:
                line = line_entry["content"]
                for match in LoaderConstants.RE_LINK_INTEGRITY.finditer(line):
                    url = match.group(2)

                    if not url or url.startswith('http') or url.startswith('#'):
                        continue

                    filename = os.path.basename(url.split('#')[0])

                    if not filename.lower().endswith('.md'):
                        continue

                    if filename.lower() == 'references.md':
                        continue

                    if filename not in self.project_index:
                        self.warnings.append({
                            "line": line_entry["line"],
                            "msg": f"Linked file '{filename}' not found in project."
                        })

    def check_alias_consistency(self) -> None:
        """
        Ensures link labels are recognized aliases of the target (Rule 28).
        Only applies to A-Z group documents (link catalogue pages).
        """
        if not any(h.is_group for h in self.doc.headings):
            return

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


    def check_citation_keys(self) -> None:
        """
        Validates that citation keys (e.g. [MUN'17]) used in links to References.md
        actually exist as entries in that file.
        """
        if not self.references_content:
            return

        for heading in self.doc.headings:
            for line_entry in heading.content.raw_lines:
                line = line_entry["content"]
                for match in LoaderConstants.RE_LINK_INTEGRITY.finditer(line):
                    label = match.group(1)
                    url = match.group(2)
                    if os.path.basename(url.split('#')[0]).lower() == 'references.md':
                        if label not in self.references_content:
                            self.warnings.append({
                                "line": line_entry["line"],
                                "msg": f"Citation key '{label}' not found in References.md."
                            })

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Runs all link-related validation rules.

        Returns:
            List[Dict[str, Any]]: A list of warning dictionaries, each containing
                'line' and 'msg' keys.
        """
        self.warnings = []
        self.check_reciprocal_links()
        self.check_link_targets()
        self.check_alias_consistency()
        self.check_citation_keys()
        return self.warnings