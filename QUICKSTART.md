# Quick Start Guide

## Installation (macOS)

### 1. Ensure Python 3.10+ is installed

```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/macos/).

### 2. Clone or download this repository

```bash
cd /path/to/Ultimate-Photo-Metadata-Manipulator
```

### 3. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Run the application

**Option A: Using the quick start script**

```bash
chmod +x run.sh
./run.sh
```

**Option B: Manual run**

```bash
cd src
python3 main.py
```

---

## Running Tests

To run the unit tests:

```bash
python3 -m pytest tests/test_metadata_handler.py -v
```

Or with unittest:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## Features

### ✓ View Metadata
1. Click "Open Image" button or press `Ctrl+O`
2. Select a JPEG, PNG, TIFF, GIF, or BMP image
3. Metadata displays in organized sections (EXIF, XMP, General)

### ✓ Clear All Metadata
1. Open an image
2. Click "Clear All" button
3. Choose to save as new file or overwrite original
4. Cleaned image is saved without any metadata

### ✓ Manage Templates
1. Click "Templates" button
2. Create new templates or manage existing ones
3. Templates are saved locally for reuse

### ✓ Export Metadata
1. Open an image
2. Go to **Metadata** menu → **Export as JSON** or **Export as TXT**
3. Save metadata to a file for review or sharing

---

## Project Structure

```
src/
├── __init__.py               # Package initialization
├── main.py                   # Main GUI application (wxPython)
├── metadata_handler.py       # Core metadata operations
└── templates.py              # Template management system

tests/
└── test_metadata_handler.py  # Unit tests

data/                        # Sample images (add your test images here)
requirements.txt             # Python dependencies
run.sh                        # Quick start script
README.md                     # Full documentation
```

---

## Troubleshooting

### wxPython installation issues

If you encounter issues installing wxPython, try:

```bash
pip3 install --upgrade pip
pip3 install wxPython --upgrade
```

For Apple Silicon (M1/M2) Macs, you may need:

```bash
pip3 install wxPython --pre
```

### Permission denied on run.sh

Make the script executable:

```bash
chmod +x run.sh
```

### Metadata not reading

Ensure the image file is in a supported format (JPEG, PNG, TIFF, GIF, BMP).

---

## Next Steps

- Add sample images to the `data/` folder for testing
- Customize templates for your workflow
- Contribute enhancements via GitHub

---

Enjoy using Photo Metadata Manipulator! 📸
