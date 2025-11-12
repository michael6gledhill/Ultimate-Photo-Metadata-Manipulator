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
- macOS 10.13 or higher
- Python 3.8 or higher
- pip3 (comes with Python)
- Homebrew (package manager)

### Quick Install

**Step 1: Install Homebrew (if not already installed)**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install Xcode Command Line Tools**

```bash
xcode-select --install
```

**Step 3: Clone the Repository**

```bash
cd ~/Documents
git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git
cd Ultimate-Photo-Metadata-Manipulator
```

**Step 4: Install Python Dependencies**

```bash
pip3 install -r requirements.txt
```

**Step 5: Run the Application**

```bash
./run.sh
```

Or manually:

```bash
cd src
python3 main.py
```

---

## Build a Standalone macOS App Bundle

You can package the application into a self‑contained `.app` using **PyInstaller**. This lets you distribute it like a normal macOS application.

### Before You Build (macOS Prerequisites)

Make sure these are in place first:

1. Xcode Command Line Tools installed (`xcode-select --install`).
2. Xcode license accepted (required for the `lipo` tool used during build). Run:
  ```bash
  sudo xcodebuild -license accept
  ```
  If the interactive viewer opens instead, scroll to the end and type `agree`.
3. A supported Python version. wxPython may lag behind the newest Python releases; if you hit issues on 3.14+, try Python 3.11 or 3.12.
4. An icon file (`logo.icns`) or a source PNG (`icon.png`) you can convert.
5. A clean virtual environment (recommended) to avoid stray packages.

### 1. Install PyInstaller (development only)

Add (or install) PyInstaller:

```bash
pip3 install pyinstaller
```

Or add to `requirements.txt` (optional for dev):

```
# Dev packaging
pyinstaller>=6.0.0
```

### 2. (Optional) Create / Update an Application Icon

If you already have `logo.icns` in the project root you can skip this.

1. Create a 1024x1024 PNG named `icon.png`.
2. Convert it to `.icns`:

```bash
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
cp icon.png icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o logo.icns
rm -r icon.iconset
```

Result: `logo.icns` in the project root.

### 3. Run PyInstaller

From the project root (using the one-line command or the multi-line form):

```bash
pyinstaller --name "PhotoMetadataManipulator" --windowed --icon logo.icns --add-data "src:src" src/main.py
```

Or multi-line for readability:

```bash
pyinstaller \
  --name "PhotoMetadataManipulator" \
  --windowed \
  --icon logo.icns \
  --add-data "src:src" \
  src/main.py
```

Explanation:
- `--windowed` hides the terminal window.
- `--add-data "src:src"` bundles the `src` package (format is `source:dest` on macOS/Linux).
- Adjust name/icon as desired.

Output appears in `dist/PhotoMetadataManipulator.app`.

### 4. Test the .app

```bash
open dist/PhotoMetadataManipulator.app
```

If Gatekeeper blocks it, right‑click → Open the first time.

### 5. (Optional) Codesign for Distribution

Use your Developer ID Certificate (requires Apple developer account):

```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  dist/PhotoMetadataManipulator.app
```

You can notarize for wider distribution (advanced—see Apple docs):

```bash
xcrun notarytool submit dist/PhotoMetadataManipulator.app \
  --apple-id YOUR_APPLE_ID --team-id TEAMID --password APP_SPECIFIC_PASSWORD \
  --wait
```

Staple ticket:

```bash
xcrun stapler staple dist/PhotoMetadataManipulator.app
```

### 6. Create a DMG (Optional)

```bash
hdiutil create -volname PhotoMetadataManipulator -srcfolder dist/PhotoMetadataManipulator.app -ov -format UDZO PhotoMetadataManipulator.dmg
```

Distribute the `.dmg` file.

### 7. Common Packaging & Build Issues

| Issue | Fix |
|-------|-----|
| `SystemError: lipo ... error code 69` with Xcode license message | Run `sudo xcodebuild -license accept` then rebuild. |
| App opens then closes immediately | Rebuild without `--windowed` to surface console errors. |
| Missing libxmp/piexif at runtime | Add hidden imports: `--hidden-import python_xmp_toolkit --hidden-import piexif`. |
| Resources not found | Confirm `--add-data "src:src"` (format is source:dest). |
| Icon not showing | Ensure file is `logo.icns` in project root; clear `dist/` and rebuild. |
| Icon generation warnings: `icon.png not a valid file` | Verify `icon.png` exists in current directory before running `sips` commands. |
| wxPython build/runtime issues on latest Python (e.g. 3.14) | Use a supported version (Python 3.11 or 3.12) until binaries catch up. |
| Gatekeeper blocks unsigned app | Right‑click → Open once, or codesign & notarize (see step 5). |


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

## Keyboard Shortcuts

- `Ctrl+O` — Add photos to queue
- `Ctrl+Q` — Exit application

---

## Troubleshooting

### Window appears blank until resized
The app now includes automatic layout finalization. If this issue persists, try:
- Updating to the latest wxPython version
- Running on a different display/resolution

### Build fails with `lipo` error / Xcode license
Accept the Xcode license:
```bash
sudo xcodebuild -license accept
```
Then re-run PyInstaller.

### Warnings: `Could not initialize cikl2metal preamble file`
These are benign macOS GPU/Metal initialization warnings seen on some systems. They do not affect functionality. Update macOS and GPU drivers (system update) if they persist; otherwise ignore.

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