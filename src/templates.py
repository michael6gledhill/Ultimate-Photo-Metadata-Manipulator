"""
Template Manager Module
Handles creation, saving, loading, and applying metadata templates.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class TemplateManager:
    """Manage metadata templates for batch operations."""

    def __init__(self, templates_dir: str = None):
        """
        Initialize the template manager.
        templates_dir: directory to store template JSON files.
        """
        self.templates_dir = templates_dir or Path.home() / '.metadata_manipulator' / 'templates'
        self.templates_dir = Path(self.templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}
        self.last_error = None

    def create_template(self, name: str, metadata: Dict[str, Any],
                        description: str = "") -> bool:
        """
        Create a new metadata template.
        name: template name (e.g., "Portfolio Upload")
        metadata: dict with metadata fields (exif, xmp, iptc, etc.)
        description: optional description
        """
        try:
            template_data = {
                'name': name,
                'description': description,
                'created': datetime.now().isoformat(),
                'metadata': metadata
            }
            self.templates[name] = template_data
            return self.save_template(name, template_data)
        except Exception as e:
            self.last_error = f"Error creating template: {str(e)}"
            return False

    def save_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """Save a template to disk."""
        try:
            template_path = self.templates_dir / f"{name}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            return True
        except Exception as e:
            self.last_error = f"Error saving template: {str(e)}"
            return False

    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a template from disk."""
        try:
            template_path = self.templates_dir / f"{name}.json"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            self.last_error = f"Template not found: {name}"
            return None
        except Exception as e:
            self.last_error = f"Error loading template: {str(e)}"
            return None

    def list_templates(self) -> List[str]:
        """Get list of all available template names."""
        try:
            templates = [f.stem for f in self.templates_dir.glob("*.json")]
            return sorted(templates)
        except Exception as e:
            self.last_error = f"Error listing templates: {str(e)}"
            return []

    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        try:
            template_path = self.templates_dir / f"{name}.json"
            if template_path.exists():
                template_path.unlink()
                if name in self.templates:
                    del self.templates[name]
                return True
            self.last_error = f"Template not found: {name}"
            return False
        except Exception as e:
            self.last_error = f"Error deleting template: {str(e)}"
            return False

    def get_template_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata from a template."""
        template = self.load_template(name)
        if template:
            return template.get('metadata', {})
        return None

    def export_templates(self, export_path: str) -> bool:
        """Export all templates as a single JSON file."""
        try:
            templates_data = {}
            for name in self.list_templates():
                template = self.load_template(name)
                if template:
                    templates_data[name] = template

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, indent=2)
            return True
        except Exception as e:
            self.last_error = f"Error exporting templates: {str(e)}"
            return False

    def import_templates(self, import_path: str) -> bool:
        """Import templates from a JSON file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)

            for name, template in templates_data.items():
                self.save_template(name, template)
            return True
        except Exception as e:
            self.last_error = f"Error importing templates: {str(e)}"
            return False
