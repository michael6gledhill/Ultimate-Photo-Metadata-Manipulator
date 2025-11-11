# Ultimate Photo Metadata Manipulator — App Outline

A powerful, open-source desktop application for reading, editing, removing, and managing photo metadata.  
Built in Python 3.14.0 with a modern GUI (planned: wxPython or PyGObject).

---

## 1. Core Features

### 1.1 Metadata Viewing
- Open and inspect metadata for supported file types:
  - **Supported formats:** JPEG / JPG, PNG, TIFF, RAW (CR2, NEF, ARW, DNG)
- Display organized metadata categories:
  - EXIF (camera data, timestamps, GPS, etc.)
  - IPTC (titles, descriptions, copyright)
  - XMP (extended metadata and edit history)
- Option to export metadata as `.json` or `.txt`.

### 1.2 File Compatibility Handling
- When an unsupported file type is opened:
  - Option **1:** Convert the file to a supported image format (e.g., `.jpg` or `.png`).
    - Uses Pillow for high-quality, non-destructive conversion.
    - Preserves the original file by default.
  - Option **2:** Skip conversion and display a notice:
    - “Unsupported file type — metadata cannot be read or written.”
  - Option **3:** Remember your preference for future operations.
- Conversion logs stored in JSON-based history for transparency.

### 1.3 Metadata Deletion
- **Delete all metadata** from a photo (clean export option).
- **Delete specific metadata fields** (e.g., GPS, author, timestamps).
- Batch-delete metadata from multiple files at once.
- Option to overwrite original files or save as new clean copies.

### 1.4 Metadata Editing / Adding
- Add or edit any metadata tag (EXIF/IPTC/XMP).
- Freeform text fields and structured metadata editors.
- Metadata validation to ensure proper encoding and format.
- Real-time preview before applying changes.

### 1.5 Metadata Templates
- Create, name, and save **metadata templates** for reuse.
  - Example templates: “Portfolio Upload”, “Client Delivery”, “Personal Archive”.
- Apply templates to single or multiple images.
- Import/export templates as `.json` files.
- Manage all templates in a dedicated Template Manager screen.

### 1.6 Persistent Storage
- All templates, settings, and file history stored locally in:
