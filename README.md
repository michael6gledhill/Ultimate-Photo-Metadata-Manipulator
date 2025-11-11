# Ultimate Photo Metadata Manipulator

A powerful, open-source tool for reading, editing, and managing photo metadata.

Everything you need for this project is free and open-source.

---

## Installation (macOS)

### Requirements
- Xcode Command Line Tools (recommended)
- For the full Xcode IDE, you can install Xcode from the App Store.
- Python 3.14 or higher
- pip3
- wxPython

---

## 1. Install required tools

### Install Xcode Command Line Tools (recommended)
The Command Line Tools are usually sufficient for many development tasks and are quick to install:

1. Press `Cmd + Space` to open Spotlight Search, type `Terminal`, and press `Enter`.
2. Open Terminal and run:

	```bash
	xcode-select --install
	```

3. Follow the prompts to complete the installation.

### Install Python and Pip
1. Download the latest version of Python from [python.org](https://www.python.org/downloads/macos/) and follow the instructions to install it.
2. Go to the "**Downloads**" section of the website and click on the button below "**Download for macOS**" to start the download.
3. Launch the downloaded `.pkg` file and follow the installation instructions.
4. Once Python is installed, move the Python installer to the Trash.

### Install wxPython
1. Open Terminal and run:

	```bash
	pip3 install --upgrade pip
	pip3 install wxPython
	```

---

---

## Project Structure

```
Ultimate-Photo-Metadata-Manipulator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # wxPython GUI application
│   ├── metadata_handler.py     # Core metadata reading/editing
│   └── templates.py            # Template manager for batch operations
├── data/                       # Sample images and templates
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── app.outline.md              # Project outline and feature roadmap
```

---

## Getting Started

### Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 2: Run the Application

```bash
cd src
python3 main.py
```

### Features

#### 1. **View Metadata**
- Open any supported image format (JPEG, PNG, TIFF, GIF, BMP)
- View organized EXIF, XMP, and general metadata
- Export metadata as JSON or TXT files

#### 2. **Clean & Delete Metadata**
- Remove all metadata at once
- Delete specific metadata fields
- Save cleaned images with a new filename or overwrite original

#### 3. **Edit Metadata**
- Add or modify EXIF, XMP, and IPTC metadata
- Real-time validation and preview

#### 4. **Metadata Templates**
- Create reusable templates (e.g., "Portfolio Upload", "Client Delivery")
- Apply templates to single or batch images
- Import/export templates as JSON

#### 5. **Batch Operations**
- Process multiple images at once
- Apply templates across multiple files

---

## Usage Examples

### Open and View Image Metadata

1. Click **"Open Image"** button or use `Ctrl+O`
2. Select an image file
3. Metadata appears in the right panel organized by section (EXIF, XMP, General)

### Clear All Metadata

1. Open an image
2. Click **"Clear All"** button
3. Choose to save as new file or overwrite original
4. Cleaned image is saved without any metadata

### Create and Apply Templates

1. Click **"Templates"** button
2. Create a new template with a name (e.g., "Portfolio Upload")
3. Define metadata to include (copyright, author, keywords)
4. Apply template to images for consistent metadata

### Export Metadata

1. Open an image
2. Go to **Metadata** menu → **Export as JSON** or **Export as TXT**
3. Choose destination and save

---

## Supported Image Formats

- **JPEG / JPG** ✓
- **PNG** ✓
- **TIFF** ✓
- **GIF** ✓
- **BMP** ✓

RAW formats (CR2, NEF, ARW, DNG) require additional libraries and are marked for future enhancement.

---

## Technical Details

### Dependencies

- **Pillow** — Image processing and manipulation
- **piexif** — EXIF data reading and writing
- **pyxmp** — XMP metadata handling
- **wxPython** — Cross-platform GUI

### Architecture

- **MetadataHandler** — Core metadata operations (read, edit, delete)
- **TemplateManager** — Template creation, storage, and application
- **MainFrame** — wxPython GUI with file browser and metadata viewer
- **TemplateDialog** — Template management interface

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## Future Enhancements

- Support for RAW image formats (CR2, NEF, ARW, DNG)
- Batch processing with progress bar
- Advanced metadata search and filtering
- GUI customization and theming
- Metadata comparison between images
- Automated metadata cleanup profiles

---

## License

This project is open-source and free to use. See `LICENSE` file for details.

---

## Support

For issues, questions, or feature requests, please open an issue on GitHub.