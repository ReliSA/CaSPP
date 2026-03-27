import sys
import os
from template_loader import TemplateLoader

class FileMatcher:
    """
    parses the file path to find the parent directory.
    Based on the parent directory it matches witha proper template.
    """
    def __init__(self, loader):
        self.loader = loader

        # Definition of pairing between folders and tamplates.
        self.folder_types = {
            "categories": "template-category",
            "forms": "template-form",
            "methodologies": "template-methodology",
            "modes": "template-mode",
            "perspectives": "template-perspective",
            "publications": "template-publication",
            "stages":"template-stage",
            "patterns": "template-pattern"
        }

    def match(self, file_path):

        # Getting the name of a parent directory from the file path

        normalized_path = file_path.replace("\\", "/")
        path_parts = normalized_path.split("/")
        if len(path_parts) < 2:
            return None
        
        parent_folder = path_parts[-2]

         
        # Matching with coresponding template
        # If there isn't a coresponding template, return None
        
        if parent_folder == "catalogue":
            template_name = "template-pattern"
        else:
            template_name = self.folder_types.get(parent_folder)
            
        if template_name:
            return self.loader.get_template(template_name)
        
        return None