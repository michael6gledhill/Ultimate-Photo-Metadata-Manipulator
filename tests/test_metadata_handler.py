"""
Unit tests for metadata_handler.py
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metadata_handler import MetadataHandler


class TestMetadataHandler(unittest.TestCase):
    """Test cases for MetadataHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = MetadataHandler()

    def test_supported_formats(self):
        """Test supported format detection."""
        self.assertTrue(self.handler.is_supported("image.jpg"))
        self.assertTrue(self.handler.is_supported("image.jpeg"))
        self.assertTrue(self.handler.is_supported("image.png"))
        self.assertTrue(self.handler.is_supported("image.TIFF"))
        self.assertFalse(self.handler.is_supported("document.pdf"))
        self.assertFalse(self.handler.is_supported("video.mp4"))

    def test_file_extension(self):
        """Test file extension extraction."""
        self.assertEqual(self.handler.get_file_extension("image.jpg"), ".jpg")
        self.assertEqual(self.handler.get_file_extension("photo.JPEG"), ".jpeg")
        self.assertEqual(self.handler.get_file_extension("/path/to/image.png"), ".png")

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        result = self.handler.read_metadata("/nonexistent/path/image.jpg")
        self.assertEqual(result, {})
        self.assertIn("File not found", self.handler.last_error)

    def test_unsupported_format(self):
        """Test handling of unsupported file formats."""
        result = self.handler.read_metadata("document.pdf")
        self.assertEqual(result, {})
        self.assertIn("Unsupported file format", self.handler.last_error)


class TestTemplateManager(unittest.TestCase):
    """Test cases for TemplateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from templates import TemplateManager
        
        self.temp_dir = tempfile.mkdtemp()
        self.manager = TemplateManager(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_template(self):
        """Test template creation."""
        metadata = {"copyright": "© 2024", "author": "Test Author"}
        result = self.manager.create_template("TestTemplate", metadata)
        self.assertTrue(result)

    def test_list_templates(self):
        """Test listing templates."""
        self.manager.create_template("Template1", {})
        self.manager.create_template("Template2", {})
        templates = self.manager.list_templates()
        self.assertIn("Template1", templates)
        self.assertIn("Template2", templates)

    def test_delete_template(self):
        """Test template deletion."""
        self.manager.create_template("ToDelete", {})
        result = self.manager.delete_template("ToDelete")
        self.assertTrue(result)
        self.assertNotIn("ToDelete", self.manager.list_templates())


if __name__ == '__main__':
    unittest.main()
