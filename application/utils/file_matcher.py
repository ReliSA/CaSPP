import os

from utils.constants import FileMatcherConstants
from utils.facets_index_template import make_facets_index_rules, make_publications_index_rules


class FileMatcher:
    """
    parses the file path to find the parent directory.
    Based on the parent directory it matches with a proper template.

    Attributes:
        loader: Instance of TemplateLoader.
        folder_types: Dictionary for pairing of folders and templates.
    """
    def __init__(self, loader):
        """Initializes FileMatcher with a template loader.

        Args:
            loader: The loader value.
        """
        self.loader = loader
        self._facets_index_template = make_facets_index_rules()
        self._publications_index_template = make_publications_index_rules()

        # Definition of pairing between folders and tamplates.
        self.folder_types: dict[str, str] = {
            "categories": "template-category",
            "forms": "template-form",
            "methodologies": "template-methodology",
            "modes": "template-mode",
            "perspectives": "template-perspective",
            "publications": "template-publication",
            "stages": "template-stage",
            "patterns": "template-pattern"
        }

    def match(self, file_path):
        """Finds the corresponding template, based on the filepath.

        Args:
            file_path: Full or relative file path.

        Returns:
            Object of template from loader or None, if no match is found.
        """
        normalized_path = file_path.replace("\\", "/")
        path_parts = normalized_path.split("/")
        if len(path_parts) < FileMatcherConstants.MIN_PATH_PARTS:
            return None

        stem = os.path.splitext(path_parts[-1])[0]
        parent_folder = path_parts[-2]

        # Facets index file: named same as its parent folder, inside catalogue/facets/
        if (stem == parent_folder
                and len(path_parts) > 2
                and path_parts[-3] == FileMatcherConstants.FACETS_FOLDER):
            if stem == "publications":
                return self._publications_index_template
            return self._facets_index_template

        if parent_folder == FileMatcherConstants.CATALOGUE_PARENT_FOLDER:
            template_name = "template-pattern"
        else:
            template_name = self.folder_types.get(parent_folder)
            if template_name is None and len(path_parts) > 2:
                grandparent_folder = path_parts[-3]
                template_name = self.folder_types.get(grandparent_folder)

        if template_name:
            return self.loader.get_template(template_name)

        return None