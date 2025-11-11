# Quick Start: Batch Metadata Editing

## Launch the App

```bash
cd /Users/michael/Documents/GitHub/Ultimate-Photo-Metadata-Manipulator
./run.sh
```

Or manually:
```bash
cd src
python3 main.py
```

## First Time Setup

1. **Install dependencies** (if not already done):
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Launch the app** using the command above

## Basic Workflow

### Step 1: Add Photos
- **Drag and drop** photos from Finder into the "Photo Queue" panel (left side)
- Or use **File > Add Photos** menu

### Step 2: Review Metadata
- **Hover your mouse** over any photo in the queue
- A **tooltip** appears showing up to 5 key metadata fields
- This lets you preview what's currently in each photo

### Step 3: Choose Template or Edit
**Option A - Use a Template:**
- Select a template from the **"Template:" dropdown** (center panel)
- Editor fields auto-fill with template values
- Jump to Step 5

**Option B - Edit Manually:**
- Fill in metadata fields:
  - **Title**: Main title/description
  - **Subject**: Category or topic
  - **Tags**: Comma-separated keywords
  - **Comments**: Multi-line notes
  - **Authors**: Photographer name(s) (semicolon-separated)
  - **Copyright**: Copyright notice

### Step 4: Preview Before Applying
- Review your edits in the editor
- If using a template, you can still modify any field

### Step 5: Apply to All Photos
- Click **"Apply Metadata to All Photos"** button (right panel)
- Confirm the action in the dialog
- ✓ Metadata written to all photos in queue

### Step 6: Optional - Batch Rename
- Click **"Batch Rename Photos"** button
- Enter a **pattern** (e.g., `CAP_Event_{index}`)
- Set **start index** (e.g., 1)
- Set **zero-padding** width (e.g., 3 → files named photo_001, photo_002, ...)
- Choose **case**: as-is / lower / upper / title
- Preview shows first 3 renamed files
- Click OK → all photos renamed

### Step 7: Save as Template (Optional)
- If you want to reuse these metadata values:
- Click **"Save as Template"** button
- Enter a **template name** (e.g., "Civil Air Patrol 2025")
- Template saved for future use

## Common Operations

### Clean All Metadata from Photos
1. Add photos to queue
2. Click **"Delete All Metadata"** button
3. Confirm
4. ✓ All EXIF/XMP tags removed

### Apply Same Metadata to Different Batches
1. Set up and apply metadata to first batch of photos
2. Click **"Save as Template"** to save current values
3. Clear queue (remove all photos)
4. Add new batch of photos
5. Load template from dropdown
6. Click **"Apply Metadata to All Photos"**

### Update an Existing Template
1. Load template from dropdown
2. Edit fields as desired
3. Click **"Save as Template"** → it updates the existing template

## Example: Real-World Scenario

**Scenario**: You have 50 photos from a Civil Air Patrol event. You want to:
1. Add metadata (event name, photographer, tags)
2. Rename all with pattern `CAP_Event_001`, `CAP_Event_002`, etc.
3. Save for future events

**Steps**:
1. Launch app → **File > Add Photos** → select all 50 JPEGs
2. Hover over a couple to verify no metadata exists
3. **Metadata Editor** fill in:
   - Title: "Civil Air Patrol Summer Training 2025"
   - Subject: "Training Event"
   - Tags: "Civil Air Patrol, Kentucky Wing, Cadets"
   - Authors: "Your Name"
   - Copyright: "Copyright 2025 Civil Air Patrol"
4. Click **"Save as Template"** → name it "CAP Event 2025"
5. Click **"Apply Metadata to All Photos"** → confirm
6. Click **"Batch Rename Photos"**:
   - Pattern: `CAP_Summe_Training_{index}`
   - Start: 1
   - Zero-pad: 3
   - Case: upper
   - Preview shows:
     - `CAP_SUMMER_TRAINING_001.jpg`
     - `CAP_SUMMER_TRAINING_002.jpg`
     - `CAP_SUMMER_TRAINING_003.jpg`
   - Click OK
7. ✓ All 50 photos renamed and metadata applied!
8. For next CAP event, just load "CAP Event 2025" template and apply to new batch

## Troubleshooting

### App Won't Launch
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip3 install wxPython piexif python-xmp-toolkit

# Then try running
./run.sh
```

### Metadata Not Visible After Applying
- Some programs (Photos.app, Preview) may cache metadata
- Try:
  - Quit and reopen the image viewer
  - Use **Image > Reload** in some apps
  - Check with `exiftool` command line tool:
    ```bash
    exiftool /path/to/photo.jpg | grep -i "title\|subject\|artist"
    ```

### Template Not Saving
- Check folder permissions: `~/.photo_metadata_templates/`
- Should be readable/writable:
  ```bash
  ls -la ~/.photo_metadata_templates/
  ```

## Keyboard Shortcuts

- **Ctrl+O**: Add Photos
- **Ctrl+Q**: Exit app
- Others coming soon!

## More Help

- See `BATCH_WORKFLOW.md` for detailed feature documentation
- README.md has installation and troubleshooting info

---

**Happy batch editing! 📸✨**
