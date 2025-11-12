# Ultimate Photo Metadata Manipulator

A powerful desktop application for batch editing photo metadata with an intuitive GUI. Built with wxPython and packaged with PyInstaller for macOS and Windows.

Everything in this project is free and open‑source.

---

## 🚀 Quick Start (macOS)

Follow these five easy steps if you're new to this.

### 1) Download the app folder
Two options:
- Option A (easiest): Click the green "Code" button → Download ZIP → unzip it
- Option B (Terminal):
  ```bash
  cd ~/Documents
  git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git
  cd Ultimate-Photo-Metadata-Manipulator
  ```

### 2) Install Xcode Command Line Tools
```bash
xcode-select --install
```
Click Install when prompted. This can take 5–10 minutes.

### 3) Install Python (if you don't have it)
- Go to https://www.python.org/downloads/
- Download the latest Python 3.x (3.11/3.12 recommended)
- Run the installer and ensure “Add to PATH”/framework install is enabled

### 4) Install required libraries
```bash
cd ~/Documents/Ultimate-Photo-Metadata-Manipulator
pip3 install -r requirements.txt
```

### 5) Run the app
```bash
python3 src/main.py
```
The app window should open.

---

## 🪟 Quick Start (Windows)

### 1) Download the app folder
- Click the green "Code" button → Download ZIP → unzip it to your Documents

### 2) Install Python
- Download Python 3.11/3.12 from https://www.python.org/downloads/
- IMPORTANT: Check “Add Python to PATH” during install

### 3) Install required libraries
Open PowerShell or Command Prompt and run:
```cmd
cd %USERPROFILE%\Documents\Ultimate-Photo-Metadata-Manipulator
pip install -r requirements.txt
```

### 4) Run the app
```cmd
python src\main.py
```

---

## 🎯 How to Use

1. Add Photos: Drag photos into the left panel or use File → Add Photos
2. Edit Metadata: Fill Headline, Description, Creator, Subject, Rights
3. Apply to All: Click “Apply Metadata to All Photos” on the right
4. Done: Your photos are updated

### Templates
- Save a set of fields: “Save As New Template” → name it
- Reuse later: pick from the dropdown
- Update or delete templates as needed

### Viewing Metadata
- Click any photo to view its metadata
- Right‑click the preview image for a full metadata view
- The display updates live every ~0.5 seconds

---

## 💡 FAQ

- The app closes immediately
  - Usually missing packages. Re‑run: `pip3 install -r requirements.txt`
  - Try launching from Terminal to see errors.

- “command not found”
  - Ensure Python 3 is installed; try `python3` instead of `python` on macOS.

- Will this modify my image pixels?
  - No. Only metadata is modified; the image content is untouched.

- Does it work on Windows?
  - Yes. See the Windows quick start above.

---

## Features

### 🖼️ Batch Photo Management
- Drag‑and‑drop queue
- Thumbnails and quick metadata preview
- Process hundreds of photos

### ✏️ Metadata Editor
- Edit Headline, Description, Creator, Subject, Rights
- Auto‑populate from the selected photo
- Apply to all photos or only the selected one
- Real‑time preview

### 📋 Templates
- Create, update, delete reusable templates
- Quick selection from a dropdown

### ⚡ Batch Operations
- Apply metadata to all
- Delete all metadata
- Batch Rename (pattern with {index}, prefix, suffix, find & replace, increment)
- Clear metadata from selected

### 🔧 Advanced
- Progress dialogs with cancel support
- Case transforms (as‑is, lower, upper, title)
- Zero‑padding for numbering
- Writes EXIF and XMP (with built‑in XMP fallback)
- Preserves camera/technical metadata
- UTF‑16LE decoding for Windows fields
- GPS DMS ↔ decimal conversion

---

## 🏗️ Build a Standalone macOS App (.app)

You can package the app as a standard macOS .app using PyInstaller.

### Prerequisites
- Xcode Command Line Tools installed: `xcode-select --install`
- Accept Xcode license (required for lipo):
  ```bash
  sudo xcodebuild -license accept
  ```
- Python 3.11/3.12 recommended (wxPython may lag on newest Python)
- Optional: `logo.icns` in project root for app icon

### Build with the helper script (recommended)
From the project root:
```bash
# Build for your current CPU
scripts/build_mac.sh --arch current

# Or target a specific architecture
scripts/build_mac.sh --arch arm64   # Apple Silicon
scripts/build_mac.sh --arch x86_64  # Intel
```
Output: `dist/current/PhotoMetadataManipulator.app`

### Run PyInstaller directly (advanced)
```bash
pyinstaller \
  --name "PhotoMetadataManipulator" \
  --windowed \
  --icon logo.icns \
  --paths src \
  src/main.py
```
- `--windowed` hides the console
- `--paths src` tells PyInstaller where to find your local modules

### Test the app
```bash
open dist/PhotoMetadataManipulator.app
```
If Gatekeeper blocks it, right‑click → Open once.

### (Optional) Codesign and Notarize
Codesign:
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  dist/PhotoMetadataManipulator.app
```
Notarize (see Apple docs for credentials):
```bash
xcrun notarytool submit dist/PhotoMetadataManipulator.app \
  --apple-id YOUR_APPLE_ID --team-id TEAMID --password APP_SPECIFIC_PASSWORD \
  --wait
xcrun stapler staple dist/PhotoMetadataManipulator.app
```

### Common macOS packaging issues
| Issue | Fix |
|------|-----|
| `SystemError: lipo ... error code 69` | Run `sudo xcodebuild -license accept` then rebuild |
| App opens then closes | Rebuild without `--windowed` to see console errors |
| `libxmp` missing | Optional; app falls back to built‑in XMP. Install `python-xmp-toolkit` if needed |
| `piexif` missing | Ensure `pip3 install -r requirements.txt` completed |
| Resources not found | Ensure `--paths src` is included |
| Icon not showing | Ensure `logo.icns` exists; clear `dist/` and rebuild |
| wxPython issues on latest Python | Use Python 3.11/3.12 |

---

## 🪟 Build a Standalone Windows EXE

### Prerequisites
- Windows 10/11
- Python 3.11/3.12 on PATH
- Optional icon: `logo.ico`

### Build with the helper script
From PowerShell in the project root:
```powershell
pip install pyinstaller
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```
Output: `dist\windows\PhotoMetadataManipulator.exe`

### Manual PyInstaller (advanced)
```powershell
pyinstaller --name "PhotoMetadataManipulator" --windowed --paths src src/main.py
```

### Troubleshooting (Windows)
- If the window closes immediately, rebuild with `-Debug` to surface errors
- If antivirus flags the exe, add an exception or codesign
- If wxPython wheels are unavailable, try Python 3.11/3.12

---

## User Interface Overview

Left panel: photo queue (drag‑and‑drop, preview on click)

Center: metadata editor + template dropdown

Right: actions (Apply to All/Selected, Delete All, Batch Rename)

---

## Usage Examples

### Edit multiple photos
```text
1) Drag photos into queue
2) Enter metadata or choose a template
3) Click “Apply Metadata to All Photos”
```

### Edit a single photo
```text
1) Select a photo in the queue
2) Edit fields
3) Click “Apply to Selected”
```

### Batch rename
```text
1) Add photos → Batch Rename
2) Choose mode: pattern/prefix/suffix/find&replace/increment
3) Preview → Rename All Now
```

### Create/update a template
```text
- Create: fill fields → Save As New Template → name it
- Update: pick template → edit fields → Update Selected Template
```

---

## Supported Image Formats
- JPEG/JPG ✓
- TIFF/TIF ✓
- GIF ✓
- BMP ✓

RAW formats (CR2, NEF, ARW, DNG) are planned for future releases.

---

## Technical Details

### Dependencies
- wxPython — GUI framework
- Pillow — image and thumbnail handling
- piexif — EXIF read/write
- python‑xmp‑toolkit (libxmp) — optional; built‑in XMP fallback is included

### Architecture
- `MainFrame` — main window and 3‑panel layout
- `MetadataHandler` — read/edit/delete metadata
- `TemplateManager` — CRUD for templates
- `BatchRenameDialog` — multi‑mode renamer

### Template storage
Templates are JSON files stored in:
```
~/.photo_metadata_templates/
```
Each template includes name, description, and the saved metadata fields.

---

## Contributing
- Fork the repository
- Create a branch: `git checkout -b feature/your-feature`
- Commit: `git commit -am "Add new feature"`
- Push: `git push origin feature/your-feature`
- Open a Pull Request

---

## Keyboard Shortcuts
- macOS: Cmd+O (add photos), Cmd+Q (quit)
- Windows/Linux: Ctrl+O (add photos), Ctrl+Q (quit)

---

## Troubleshooting

- Window appears blank until resized
  - Update wxPython; try a different display/scale setting

- Xcode license / lipo errors (macOS)
  ```bash
  sudo xcodebuild -license accept
  ```

- Metadata not showing
  - File may not support certain fields; verify required packages are installed
  - XMP works without libxmp (built‑in fallback)

- Templates not saving
  - Check permissions for `~/.photo_metadata_templates/`
  - Avoid invalid characters in template names

- Packaged app closes on launch
  - Rebuild with debug logging or run the binary directly to view console output
  ```bash
  DEBUG_BUILD=1 scripts/build_mac.sh --arch current
  dist/current/PhotoMetadataManipulator.app/Contents/MacOS/PhotoMetadataManipulator
  ```

---

## License
This project is open‑source and free to use. See the `LICENSE` file for details.

## Support
Questions, issues, or feature requests? Please open an issue on GitHub.

---

## Changelog
- ✅ Fixed packaged module discovery by adding `--paths src`
- ✅ Live metadata display updated every 0.5s
- ✅ Simplified core fields: Headline, Description, Creator, Subject, Rights
- ✅ Built‑in XMP fallback (no external dependency required)
- ✅ Cross‑arch build scripts (Intel, Apple Silicon)
- ✅ Windows PowerShell build script
- ✅ Improved error handling and messages
# Ultimate Photo Metadata Manipulator# Ultimate Photo Metadata Manipulator



A powerful desktop application for batch editing photo metadata with an intuitive GUI. Built with wxPython for cross-platform compatibility.A powerful desktop application for batch editing photo metadata with an intuitive GUI. Built with wxPython for cross-platform compatibility.



Everything you need for this project is free and open-source.Everything you need for this project is free and open-source.



------





Edit photo metadata (title, description, keywords, copyright, etc.) for hundreds of photos at once. Save time by applying the same information to multiple photos or using templates.- Drag-and-drop multiple photos into the queue

---- Process hundreds of images at once

## 📥 How to Download and Install (macOS)- Edit Title, Subject, Tags, Comments, Authors, and Copyright


### Super Simple 5-Step Installation- Apply metadata to all photos or individual selections

- Real-time preview of changes

### 📋 **Template System**
**Option A: Download as ZIP (Easiest)**- Delete templates you no longer need
### Super Simple 5-Step Installation
2. Click **"Download ZIP"**
3. Find the ZIP file in your Downloads folder### ⚡ **Batch Operations**

Two ways to download:

**Option A: Download as ZIP (Easiest)**
- **Batch Rename Photos** - Five rename modes:
1. Open **Terminal** (press Cmd+Space, type "terminal", press Enter)  - Add prefix to filenames
2. Copy and paste these commands one at a time:  - Add suffix to filenames
  - Find and replace text
```bash  - Increment with numbering
cd ~/Downloads- **Clear Metadata from Selected** - Remove metadata from single photo

1. Open **Terminal** (press Cmd+Space, type "terminal", press Enter)
2. Copy and paste these commands one at a time:

```bash
cd ~/Downloads
git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git
cd Ultimate-Photo-Metadata-Manipulator
```

---

**STEP 2: Install Xcode Command Line Tools**

1. Open **Terminal** (if not already open)
2. Copy and paste this command:

```bash
xcode-select --install
```

3. A popup will appear - click **"Install"**
4. Wait for it to finish (takes 5-10 minutes)

---

**STEP 3: Install Python (if you don't have it)**

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **"Download Python 3.12"** button
3. Open the downloaded file and follow the installer
4. **Important**: During installation, make sure Python gets added to your system

---

**STEP 4: Install Required Libraries**

1. Open **Terminal**
2. Navigate to the app folder:

```bash
cd ~/Downloads/Ultimate-Photo-Metadata-Manipulator
```

3. Install the required libraries:

```bash
pip3 install -r requirements.txt
```

Wait for this to finish (takes 2-5 minutes). You'll see lots of text scroll by - that's normal!

---

**STEP 5: Run the App**

Still in Terminal, type:

```bash
python3 src/main.py
```

**That's it!** The app window should open.

---

## 🎯 How to Use the App (Quick Guide)

1. **Add Photos**: Drag and drop photos into the left panel, OR click File → Add Photos
2. **Edit Metadata**: Fill in the fields in the center (Headline, Description, Creator, Subject, Rights)
3. **Apply to All**: Click "Apply Metadata to All Photos" on the right
4. **Done!** Your photos now have the metadata you entered

### Save Time with Templates

- Fill in metadata fields
- Click "Save As New Template"
- Name your template
- Next time, just select the template from the dropdown!

### View Metadata

- Click any photo in the queue to see its current metadata
- Right-click the preview image to see all metadata details
- The metadata display updates live every 0.5 seconds

---

## 💡 Common Questions

**Q: The app closed immediately after opening**
- This usually means Python libraries didn't install correctly
- Try running `pip3 install -r requirements.txt` again
- Make sure you're in the correct folder (Ultimate-Photo-Metadata-Manipulator)

**Q: I see "command not found" errors**
- You might not have Python installed correctly
- Download Python from [python.org](https://www.python.org/downloads/)
- Try using `python3` instead of `python` in commands

**Q: "xcode-select: error: command line tools are already installed"**
- Great! You already have what you need. Continue to the next step.

**Q: Can I make this into a regular Mac app I can double-click?**
- Yes! See the "Build a Standalone App" section below

**Q: Does this work on Windows?**
- Yes! See the "Windows Installation" section below

**Q: Will this delete my original photos?**
- No! This app only modifies the metadata (information about the photo), not the image itself

---

## 📦 Windows Installation

### Simple Steps for Windows Users

**STEP 1: Download This App**

1. Click the green **"Code"** button at the top of this page
2. Click **"Download ZIP"**
3. Right-click the ZIP file → Extract All
4. Move the extracted folder to your Downloads

**STEP 2: Install Python**

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.12
3. **IMPORTANT**: Check the box "Add Python to PATH" during installation
4. Click "Install Now"

**STEP 3: Install Libraries**

1. Open **Command Prompt** (press Windows key, type "cmd", press Enter)
2. Navigate to the app folder:

```cmd
cd %USERPROFILE%\Downloads\Ultimate-Photo-Metadata-Manipulator
```

3. Install libraries:

```cmd
pip install -r requirements.txt
```

**STEP 4: Run the App**

```cmd
python src\main.py
```

---

## Features

### 🖼️ **Batch Photo Management**

- Drag-and-drop multiple photos into the queue
- Visual thumbnail preview of selected photos
- Process hundreds of images at once

### ✏️ **Metadata Editor**

- Edit Headline, Description, Creator, Subject, and Rights
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

cd Ultimate-Photo-Metadata-Manipulator### 🔧 **Advanced Features**

```- Progress dialogs with cancel support

---- Zero-padding for numbered files


- Subject written to both EXIF (XPSubject) and XMP (dc:subject)
- Zero-padding for numbered files
- Writes both EXIF and XMP metadata
- Preserves camera metadata (doesn't overwrite technical info)
- Built-in XMP reader/writer (no external libraries required)
- Right-click preview to view all metadata
- Hover over queue items to see metadata preview
- UTF-16LE decoding for Windows metadata fields
- GPS coordinate conversion (DMS to decimal)



```bash```bash

cd ~/Downloads/Ultimate-Photo-Metadata-Manipulatorcd ~/Downloads

```git clone https://github.com/michael6gledhill/Ultimate-Photo-Metadata-Manipulator.git

cd Ultimate-Photo-Metadata-Manipulator

3. Install the required libraries:```


```bash**Step 4: Install Python Dependencies**

pip3 install -r requirements.txt

``````bash

Wait for this to finish (takes 2-5 minutes). You'll see lots of text scroll by - that's normal!```



---**Step 5: Run the Application**



**STEP 5: Run the App**```bash

./run.sh


```bashOr manually:

python3 src/main.py

``````bash

cd src

**That's it!** The app window should open.python3 main.py

```


---

## 🎯 How to Use the App (Quick Guide)
## Build a Standalone macOS App Bundle (Intel and Apple Silicon)

2. **Edit Metadata**: Fill in the fields in the center (Headline, Description, Creator, Subject, Rights)You can package the application into a self‑contained `.app` using **PyInstaller**. This lets you distribute it like a normal macOS application.

3. **Apply to All**: Click "Apply Metadata to All Photos" on the right

4. **Done!** Your photos now have the metadata you entered### Before You Build (macOS Prerequisites)



### Save Time with Templates

- Fill in metadata fields1. Xcode Command Line Tools installed (`xcode-select --install`).

- Click "Save As New Template"2. Xcode license accepted (required for the `lipo` tool used during build). Run:
- Name your template  ```bash

- Next time, just select the template from the dropdown!  sudo xcodebuild -license accept

  ```

### View Metadata  If the interactive viewer opens instead, scroll to the end and type `agree`.

- Click any photo in the queue to see its current metadata3. A supported Python version. wxPython may lag behind the newest Python releases; if you hit issues on 3.14+, try Python 3.11 or 3.12.
- The metadata display updates live every 0.5 seconds5. A clean virtual environment (recommended) to avoid stray packages.



## 💡 Common QuestionsAdd (or install) PyInstaller:


**Q: The app closed immediately after opening**```bash


- Try running `pip3 install -r requirements.txt` again```
- Make sure you're in the correct folder (Ultimate-Photo-Metadata-Manipulator)


**Q: I see "command not found" errors**
- You might not have Python installed correctly```

- Download Python from [python.org](https://www.python.org/downloads/)# Dev packaging


**Q: "xcode-select: error: command line tools are already installed"**

**Q: Can I make this into a regular Mac app I can double-click?**If you already have `logo.icns` in the project root you can skip this.

1. Create a 1024x1024 PNG named `icon.png`.

```bash
---sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png

## 📦 Windows Installationsips -z 128 128   icon.png --out icon.iconset/icon_128x128.png

sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png

sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png

**STEP 1: Download This App**sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png

1. Click the green **"Code"** button at the top of this pageiconutil -c icns icon.iconset -o logo.icns

2. Click **"Download ZIP"**rm -r icon.iconset

3. Right-click the ZIP file → Extract All```

4. Move the extracted folder to your Downloads

Result: `logo.icns` in the project root.

**STEP 2: Install Python**

### 3. Build with the helper script (recommended)

1. Go to [python.org/downloads](https://www.python.org/downloads/)

2. Download Python 3.12This repo includes a macOS build script that supports Intel (x86_64), Apple Silicon (arm64), and universal2 builds.

3. **IMPORTANT**: Check the box "Add Python to PATH" during installation
## 🏗️ Build a Standalone macOS App (Advanced)

### Prerequisites

1. Complete the installation steps above first
2. Accept Xcode license:

```bash
sudo xcodebuild -license accept
```

3. Install PyInstaller:

```bash
pip3 install pyinstaller
```

### Build the App

From the project folder in Terminal:

```bash
# Build for your current Mac
scripts/build_mac.sh --arch current

# Build for Apple Silicon (M1/M2/M3)
scripts/build_mac.sh --arch arm64

# Build for Intel Macs
scripts/build_mac.sh --arch x86_64
```

Your app will be in: `dist/current/PhotoMetadataManipulator.app`

### Use the App
Double-click to open, or right-click → Open the first time (for unsigned apps).

---


From PowerShell in the project folder:

```powershell
# Install PyInstaller first
pip install pyinstaller

# Build the exe
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Your executable will be in: `dist/windows/PhotoMetadataManipulator.exe`

---



**Left Panel - Photo Queue**
- Drag and drop photos or use File → Add Photos
- Click on any photo to preview and auto-load its metadata
- Hover over photos to see a quick metadata preview
- Remove selected photo from queue

**Center Panel - Metadata Editor**
- Template dropdown for quick template selection
- Thumbnail preview of selected photo
- Live metadata display (updates every 0.5 seconds)

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
4. Progress dialog shows operation status


1. Add photos to queue
### Batch Rename

1. Add photos to queue
3. Choose rename mode:
   - **Pattern**: Use `photo_{index}` format
   - **Prefix**: Add text before filename
   - **Suffix**: Add text after filename

### Create Template
4. Template is saved and selected in dropdown

### Update Template

1. Select a template from dropdown
2. Modify metadata fields as needed
3. Click **"Update Selected Template"**
4. Confirm update
---

- **BMP** ✓
RAW formats (CR2, NEF, ARW, DNG) require additional libraries and are planned for future releases.

## Technical Details
### Dependencies

- **wxPython** — Cross-platform GUI framework
- **piexif** — EXIF data reading and writing
- **python-xmp-toolkit** (libxmp) — XMP metadata handling (optional, has built-in fallback)
### Architecture

**Core Components:**
- `MainFrame` — Main application window with 3-panel layout
- `TemplateManager` — Template CRUD operations
- `BatchRenameDialog` — Multi-mode file renaming interface

- Built-in XMP reader/writer with fallback (no external dependencies required)
- UTF-16LE decoding for Windows XP metadata fields
- Rational number conversion for EXIF values
- Embedded null character removal for clean metadata
- Progress dialogs with cancel support
- Auto-layout refresh for immediate UI rendering
- Live metadata display with 0.5s refresh

### Template Storage
Templates are stored as JSON files in:
```
~/.photo_metadata_templates/
```

Each template contains:
- Template name
- Metadata fields (headline, description, creator, subject, rights)

**STEP 3: Install Libraries**```bash

# Build for your current CPU

```bash
sudo xcodebuild -license accept
```

If the interactive viewer opens instead, scroll to the end and type `agree`.


# Build for Apple Silicon (arm64)

```cmdscripts/build_mac.sh --arch arm64

cd %USERPROFILE%\Downloads\Ultimate-Photo-Metadata-Manipulator

```# Build for Intel (x86_64)

scripts/build_mac.sh --arch x86_64

3. Install libraries:

# Build universal2 (single app containing both slices)

```cmd# Requires Python "universal2" and compatible universal wheels (e.g. wxPython 4.2.x universal2)

pip install -r requirements.txtscripts/build_mac.sh --arch universal2

``````



**STEP 4: Run the App**Outputs are placed under:



```cmd```

python src\main.pydist/<arch>/PhotoMetadataManipulator.app

``````



---Notes:

- For universal2, install Python from python.org (universal2 build) and a wxPython universal2 wheel (4.2.x). If universal2 wheels are not available for your Python version, prefer two separate arch builds instead.

## Features- The script auto-detects optional packages like `libxmp`; the app works without it using a built-in XMP fallback.



### 🖼️ **Batch Photo Management**### 4. Run PyInstaller directly (advanced)

- Drag-and-drop multiple photos into the queue

- Visual thumbnail preview of selected photosFrom the project root (using the one-line command or the multi-line form):

- Live metadata display that updates every 0.5 seconds

- Process hundreds of images at once```bash

pyinstaller --name "PhotoMetadataManipulator" --windowed --icon logo.icns --add-data "src:src" src/main.py

### ✏️ **Metadata Editor**```

- Edit Headline, Description, Creator, Subject, and Rights

- Auto-populate editor with current metadata from selected photoOr multi-line for readability:

- Apply metadata to all photos or individual selections

- Real-time preview of changes```bash

pyinstaller \

### 📋 **Template System**  --name "PhotoMetadataManipulator" \

- Create and save metadata templates for reuse  --windowed \

- Update existing templates with current editor values  --icon logo.icns \

- Delete templates you no longer need  --add-data "src:src" \

- Quick template selection from dropdown  src/main.py

```

### ⚡ **Batch Operations**
pyinstaller --name "PhotoMetadataManipulator" --windowed --icon logo.icns --paths src src/main.py
- **Apply Metadata to All Photos** - Apply editor values to entire queueExplanation:

- **Delete All Metadata** - Strip all metadata from all photos- `--windowed` hides the terminal window.

- **Batch Rename Photos** - Five rename modes:- `--add-data "src:src"` bundles the `src` package (format is `source:dest` on macOS/Linux).

  - Pattern with {index} placeholder- Adjust name/icon as desired.

  - Add prefix to filenames
  --paths src \
  - Add suffix to filenamesOutput appears in `dist/PhotoMetadataManipulator.app`.

  - Find and replace text

  - Increment with numbering### 5. Test the .app
- `--paths src` tells PyInstaller where to find local modules.
- **Clear Metadata from Selected** - Remove metadata from single photo

```bash

### 🔧 **Advanced Features**open dist/PhotoMetadataManipulator.app

- Progress dialogs with cancel support```

- Case transformation (as-is, lower, upper, title)

- Zero-padding for numbered filesIf Gatekeeper blocks it, right‑click → Open the first time.

- Writes both EXIF and XMP metadata

- Preserves camera metadata (doesn't overwrite technical info)### 6. (Optional) Codesign for Distribution

- Built-in XMP reader/writer (no external libraries required)

- Right-click preview to view all metadataUse your Developer ID Certificate (requires Apple developer account):

- Hover over queue items to see metadata preview

- UTF-16LE decoding for Windows metadata fields```bash

- GPS coordinate conversion (DMS to decimal)codesign --deep --force --verify --verbose \

  --sign "Developer ID Application: Your Name (TEAMID)" \

---  dist/PhotoMetadataManipulator.app

```

## 🏗️ Build a Standalone macOS App (Advanced)

You can notarize for wider distribution (advanced—see Apple docs):

Want to create a double-clickable Mac app? Follow these steps.

```bash

### Prerequisitesxcrun notarytool submit dist/PhotoMetadataManipulator.app \

1. Complete the installation steps above first  --apple-id YOUR_APPLE_ID --team-id TEAMID --password APP_SPECIFIC_PASSWORD \

### Common Packaging & Build Issues

```bash```

sudo xcodebuild -license accept

```Staple ticket:

3. Install PyInstaller:
| Resources not found | Confirm `--paths src` is included in build command. |
```bash```bash

pip3 install pyinstallerxcrun stapler staple dist/PhotoMetadataManipulator.app

``````


## Advanced Build Details (Windows)
hdiutil create -volname PhotoMetadataManipulator -srcfolder dist/PhotoMetadataManipulator.app -ov -format UDZO PhotoMetadataManipulator.dmg

```bash```
### Prerequisites

# Build for your current Mac

scripts/build_mac.sh --arch currentDistribute the `.dmg` file.


### Build using the helper PowerShell script
# Build for Apple Silicon (M1/M2/M3)### 8. Common Packaging & Build Issues

scripts/build_mac.sh --arch arm64

| Issue | Fix |

# Build for Intel Macs|-------|-----|

scripts/build_mac.sh --arch x86_64| `SystemError: lipo ... error code 69` with Xcode license message | Run `sudo xcodebuild -license accept` then rebuild. |
Output: `dist/windows/PhotoMetadataManipulator.exe`

| Missing libxmp at runtime | Optional; the app falls back to a built-in XMP parser. If you need it, install `python-xmp-toolkit` and Homebrew `exempi`. |


| Build for the other CPU architecture | Use the build script with `--arch x86_64` or `--arch arm64`. For one-app-for-both, try `--arch universal2` with a universal2 Python/wxPython. |

pyinstaller --name "PhotoMetadataManipulator" --windowed --paths src src/main.py

| Icon not showing | Ensure file is `logo.icns` in project root; clear `dist/` and rebuild. |
### Troubleshooting (Windows)

Double-click to open, or right-click → Open the first time (for unsigned apps).| Icon generation warnings: `icon.png not a valid file` | Verify `icon.png` exists in current directory before running `sips` commands. |

| wxPython build/runtime issues on latest Python (e.g. 3.14) | Use a supported version (Python 3.11 or 3.12) until binaries catch up. |


powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1You can package the application into a standalone .exe using PyInstaller on Windows.
2. Select a template from the dropdown or enter metadata manually*Batch Actions:*

3. Click **"Apply Metadata to All Photos"**- Apply Metadata to All Photos


4. Progress dialog shows operation status- Delete All Metadata

- Batch Rename Photos

### Edit Single Photo

*Single Photo Actions:*

1. Add photos to queue- Apply to Selected
- `Ctrl+O` (or `Cmd+O` on Mac) — Add photos to queue
- `Ctrl+Q` (or `Cmd+Q` on Mac) — Exit application
2. Click on a photo in the queue (auto-loads current metadata)- Clear Metadata from Selected

3. Edit the metadata fields

4. Click **"Apply to Selected"***Templates:*


The app now includes automatic layout finalization. If this issue persists, try:

- Save As New Template

### Batch Rename- Update Selected Template


- Delete Selected Template


1. Add photos to queue


Then re-run the build script.

3. Choose rename mode:


   - **Pattern**: Use `photo_{index}` format## Usage Examples


   - **Prefix**: Add text before filename

- XMP metadata works even without libxmp installed (uses built-in fallback)

   - **Find & Replace**: Replace text in filenames1. Drag photos into the queue (left panel)


   - **Increment**: Add sequential numbers2. Select a template from the dropdown or enter metadata manually

### "ModuleNotFoundError" when running packaged app

- This has been fixed in the build scripts
- Make sure you're using the latest version of `scripts/build_mac.sh` or `scripts/build_windows.ps1`
- The scripts now include `--paths src` to find all modules correctly

### App closes immediately after opening (packaged version)

- Try rebuilding with debug mode to see errors:

```bash
DEBUG_BUILD=1 scripts/build_mac.sh --arch current
```

- Run the binary directly to see console output:

```bash
dist/current/PhotoMetadataManipulator.app/Contents/MacOS/PhotoMetadataManipulator
```

4. Preview first 3 renames3. Click **"Apply Metadata to All Photos"**

5. Click **"Rename All Now"**4. Progress dialog shows operation status



### Create Template### Edit Single Photo



1. Fill in metadata fields you want to save1. Add photos to queue

2. Click **"Save As New Template"**2. Click on a photo in the queue (auto-loads current metadata)

3. Enter template name3. Edit the metadata fields

4. Template is saved and selected in dropdown4. Click **"Apply to Selected"**




### Update Template### Batch Rename



1. Select a template from dropdown1. Add photos to queue

2. Modify metadata fields as needed2. Click **"Batch Rename Photos"**

3. Click **"Update Selected Template"**3. Choose rename mode:

4. Confirm update   - **Pattern**: Use `photo_{index}` format

   - **Prefix**: Add text before filename

---   - **Suffix**: Add text after filename

   - **Find & Replace**: Replace text in filenames

## Supported Image Formats   - **Increment**: Add sequential numbers

4. Preview first 3 renames

- **JPEG / JPG** ✓5. Click **"Rename All Now"**

- **PNG** ✓

- **TIFF / TIF** ✓### Create Template

- **GIF** ✓

- **BMP** ✓1. Fill in metadata fields you want to save

2. Click **"Save As New Template"**

RAW formats (CR2, NEF, ARW, DNG) require additional libraries and are planned for future releases.3. Enter template name

4. Template is saved and selected in dropdown

---

### Update Template

## Technical Details

1. Select a template from dropdown

### Dependencies2. Modify metadata fields as needed

3. Click **"Update Selected Template"**

- **wxPython** — Cross-platform GUI framework4. Confirm update

- **Pillow** — Image processing and thumbnail generation

- **piexif** — EXIF data reading and writing---

- **python-xmp-toolkit** (libxmp) — XMP metadata handling (optional, has built-in fallback)

- **puremagic** — Cross-platform file type detection## Supported Image Formats



### Architecture- **JPEG / JPG** ✓

- **TIFF / TIF** ✓

**Core Components:**- **GIF** ✓

- `MainFrame` — Main application window with 3-panel layout- **BMP** ✓

- `MetadataHandler` — Metadata operations (read, edit, delete)

- `TemplateManager` — Template CRUD operationsRAW formats (CR2, NEF, ARW, DNG) require additional libraries and are planned for future releases.

- `BatchRenameDialog` — Multi-mode file renaming interface

---

**Key Features:**

- Built-in XMP reader/writer with fallback (no external dependencies required)## Technical Details

- UTF-16LE decoding for Windows XP metadata fields

- Rational number conversion for EXIF values### Dependencies

- GPS DMS to decimal coordinate conversion- **wxPython** — Cross-platform GUI framework

- Embedded null character removal for clean metadata- **Pillow** — Image processing and thumbnail generation

- Progress dialogs with cancel support- **piexif** — EXIF data reading and writing

- Auto-layout refresh for immediate UI rendering- **python-xmp-toolkit** (libxmp) — XMP metadata handling

- Live metadata display with 0.5s refresh

### Architecture

### Template Storage

**Core Components:**

Templates are stored as JSON files in:- `MainFrame` — Main application window with 3-panel layout

```- `MetadataHandler` — Metadata operations (read, edit, delete)

~/.photo_metadata_templates/- `TemplateManager` — Template CRUD operations

```- `BatchRenameDialog` — Multi-mode file renaming interface



Each template contains:**Key Features:**

- Template name- UTF-16LE decoding for Windows XP metadata fields

- Description- Rational number conversion for EXIF values

- Metadata fields (headline, description, creator, subject, rights)- GPS DMS to decimal coordinate conversion

- Embedded null character removal for clean metadata

---- Progress dialogs with cancel support

- Auto-layout refresh for immediate UI rendering

## Contributing

### Template Storage

Contributions are welcome! Please:

Templates are stored as JSON files in:

1. Fork the repository```

2. Create a feature branch (`git checkout -b feature/your-feature`)~/.photo_metadata_templates/

3. Commit your changes (`git commit -am 'Add new feature'`)```

4. Push to the branch (`git push origin feature/your-feature`)

5. Open a Pull RequestEach template contains:

- Template name

---- Description

- Metadata fields (title, subject, tags, comments, authors, copyright)

## Keyboard Shortcuts

---

- `Ctrl+O` (or `Cmd+O` on Mac) — Add photos to queue

- `Ctrl+Q` (or `Cmd+Q` on Mac) — Exit application## Contributing



---Contributions are welcome! Please:

1. Fork the repository

## Troubleshooting2. Create a feature branch (`git checkout -b feature/your-feature`)

3. Commit your changes (`git commit -am 'Add new feature'`)

### Window appears blank until resized4. Push to the branch (`git push origin feature/your-feature`)

The app now includes automatic layout finalization. If this issue persists, try:5. Open a Pull Request

- Updating to the latest wxPython version

- Running on a different display/resolution---



### Build fails with `lipo` error / Xcode license## Keyboard Shortcuts

Accept the Xcode license:

```bash- `Ctrl+O` — Add photos to queue

sudo xcodebuild -license accept

```---

Then re-run the build script.

## Troubleshooting

### Warnings: `Could not initialize cikl2metal preamble file`

These are benign macOS GPU/Metal initialization warnings seen on some systems. They do not affect functionality. Update macOS and GPU drivers (system update) if they persist; otherwise ignore.### Window appears blank until resized

- Updating to the latest wxPython version

### Metadata not showing correctly- Running on a different display/resolution

- Ensure the image contains metadata (some formats don't support all fields)

- Check that you have the correct Python packages installed### Build fails with `lipo` error / Xcode license

- XMP metadata works even without libxmp installed (uses built-in fallback)Accept the Xcode license:

```bash

### Template not savingsudo xcodebuild -license accept

- Check permissions for `~/.photo_metadata_templates/` directory```

- Ensure template name doesn't contain invalid charactersThen re-run PyInstaller.



### "ModuleNotFoundError" when running packaged app### Warnings: `Could not initialize cikl2metal preamble file`

- This has been fixed in the build scriptsThese are benign macOS GPU/Metal initialization warnings seen on some systems. They do not affect functionality. Update macOS and GPU drivers (system update) if they persist; otherwise ignore.

- Make sure you're using the latest version of `scripts/build_mac.sh` or `scripts/build_windows.ps1`

- The scripts now include `--paths src` to find all modules correctly### Metadata not showing correctly

- Ensure the image contains metadata (some formats don't support all fields)

### App closes immediately after opening (packaged version)- Check that you have the correct Python packages installed

- Try rebuilding with debug mode to see errors:- For XMP metadata, ensure `libxmp` is properly installed

```bash

DEBUG_BUILD=1 scripts/build_mac.sh --arch current### Template not saving

```- Check permissions for `~/.photo_metadata_templates/` directory

- Run the binary directly to see console output:- Ensure template name doesn't contain invalid characters

```bash

dist/current/PhotoMetadataManipulator.app/Contents/MacOS/PhotoMetadataManipulator---

```

## License

---

This project is open-source and free to use. See `LICENSE` file for details.

## License---



This project is open-source and free to use. See `LICENSE` file for details.## Support



---For issues, questions, or feature requests, please open an issue on GitHub.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

## Changelog

### Recent Updates
- ✅ Fixed module discovery in packaged apps (added `--paths src`)
- ✅ Added live metadata display with 0.5s refresh
- ✅ Simplified metadata fields to: Headline, Description, Creator, Subject, Rights
- ✅ Built-in XMP fallback (no external dependencies required)
- ✅ Cross-architecture build support (Intel, Apple Silicon, Universal2)
- ✅ Windows PowerShell build script
- ✅ Improved error handling and user feedback
