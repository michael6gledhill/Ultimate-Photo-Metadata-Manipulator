# Ultimate Photo Metadata Manipulator

A powerful desktop application for batch editing photo metadata with an intuitive GUI. Built with wxPython for cross-platform compatibility.

Everything you need for this project is free and open-source.

---

## Features

### 🖼️ **Batch Photo Management**
- Drag-and-drop multiple photos into the queue
- Visual thumbnail preview of selected photos
- Process hundreds of images at once

### ✏️ **Metadata Editor**
- Edit Title, Subject, Tags, Comments, Authors, and Copyright
- Auto-populate editor with current metadata from selected photo
- Apply metadata to all photos or individual selections
- Real-time preview of changes

### 📋 **Template System**
- Create and save metadata templates for reuse
- Update existing templates with current editor values
- Delete templates you no longer need
- Quick template selection from dropdown

### ⚡ **Batch Operations**
- **Apply Metadata to All Photos** - Apply editor values to entire queue
- **Delete All Metadata** - Strip all metadata from all photos
- **Batch Rename Photos** - Five rename modes:
  - Pattern with {index} placeholder
  - Add prefix to filenames
  - Add suffix to filenames
  - Find and replace text
  - Increment with numbering
- **Clear Metadata from Selected** - Remove metadata from single photo

### 🔧 **Advanced Features**
- Progress dialogs with cancel support
- Case transformation (as-is, lower, upper, title)
- Zero-padding for numbered files
- Subject written to both EXIF (XPSubject) and XMP (dc:subject)
- UTF-16LE decoding for Windows metadata fields
- GPS coordinate conversion (DMS to decimal)

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

cd ~/

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install git

sudo port install git

xcode-select --install

git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git

cd Ultimate-Photo-Metadata-Manipulator

./run.sh

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

Or use the provided run script:

```bash
./run.sh
```

---

## User Interface

### Layout

The application has a clean 3-panel layout:

**Left Panel - Photo Queue**
- Drag and drop photos or use File → Add Photos
- Click on any photo to preview and auto-load its metadata
- Remove selected photo from queue

**Center Panel - Metadata Editor**
- Template dropdown for quick template selection
- Edit fields: Title, Subject, Tags, Comments, Authors, Copyright
- Thumbnail preview of selected photo

**Right Panel - Actions**

*Batch Actions:*
- Apply Metadata to All Photos
- Delete All Metadata
- Batch Rename Photos

*Single Photo Actions:*
- Apply to Selected
- Clear Metadata from Selected

*Templates:*
- Save As New Template
- Update Selected Template
- Delete Selected Template

---

## Usage Examples

### Edit Multiple Photos

1. Drag photos into the queue (left panel)
2. Select a template from the dropdown or enter metadata manually
3. Click **"Apply Metadata to All Photos"**
4. Progress dialog shows operation status

### Edit Single Photo

1. Add photos to queue
2. Click on a photo in the queue (auto-loads current metadata)
3. Edit the metadata fields
4. Click **"Apply to Selected"**

### Batch Rename

1. Add photos to queue
2. Click **"Batch Rename Photos"**
3. Choose rename mode:
   - **Pattern**: Use `photo_{index}` format
   - **Prefix**: Add text before filename
   - **Suffix**: Add text after filename
   - **Find & Replace**: Replace text in filenames
   - **Increment**: Add sequential numbers
4. Preview first 3 renames
5. Click **"Rename All Now"**

### Create Template

1. Fill in metadata fields you want to save
2. Click **"Save As New Template"**
3. Enter template name
4. Template is saved and selected in dropdown

### Update Template

1. Select a template from dropdown
2. Modify metadata fields as needed
3. Click **"Update Selected Template"**
4. Confirm update

---

## Supported Image Formats

- **JPEG / JPG** ✓
- **PNG** ✓
- **TIFF / TIF** ✓
- **GIF** ✓
- **BMP** ✓

RAW formats (CR2, NEF, ARW, DNG) require additional libraries and are planned for future releases.

---

## Technical Details

### Dependencies

- **wxPython** — Cross-platform GUI framework
- **Pillow** — Image processing and thumbnail generation
- **piexif** — EXIF data reading and writing
- **python-xmp-toolkit** (libxmp) — XMP metadata handling

### Architecture

**Core Components:**
- `MainFrame` — Main application window with 3-panel layout
- `MetadataHandler` — Metadata operations (read, edit, delete)
- `TemplateManager` — Template CRUD operations
- `BatchRenameDialog` — Multi-mode file renaming interface

**Key Features:**
- UTF-16LE decoding for Windows XP metadata fields
- Rational number conversion for EXIF values
- GPS DMS to decimal coordinate conversion
- Embedded null character removal for clean metadata
- Progress dialogs with cancel support
- Auto-layout refresh for immediate UI rendering

### Template Storage

Templates are stored as JSON files in:
```
~/.photo_metadata_templates/
```

Each template contains:
- Template name
- Description
- Metadata fields (title, subject, tags, comments, authors, copyright)

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

- [ ] Support for RAW image formats (CR2, NEF, ARW, DNG)
- [ ] IPTC metadata support
- [ ] Metadata comparison between images
- [ ] Advanced search and filter in photo queue
- [ ] Undo/redo functionality
- [ ] Export/import templates
- [ ] Metadata presets library
- [ ] Custom metadata fields
- [ ] Batch geolocation editing
- [ ] Metadata validation rules

---

## Keyboard Shortcuts

- `Ctrl+O` — Add photos to queue
- `Ctrl+Q` — Exit application

---

## Troubleshooting

### Window appears blank until resized
The app now includes automatic layout finalization. If this issue persists, try:
- Updating to the latest wxPython version
- Running on a different display/resolution

### Metadata not showing correctly
- Ensure the image contains metadata (some formats don't support all fields)
- Check that you have the correct Python packages installed
- For XMP metadata, ensure `libxmp` is properly installed

### Template not saving
- Check permissions for `~/.photo_metadata_templates/` directory
- Ensure template name doesn't contain invalid characters

---

## License

This project is open-source and free to use. See `LICENSE` file for details.

---

## Support

For issues, questions, or feature requests, please open an issue on GitHub.