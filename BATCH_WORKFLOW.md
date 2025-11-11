# Photo Metadata Manipulator - Redesigned Batch Workflow

## Overview
The app has been completely redesigned to support a **batch metadata editing workflow**. You can now:
1. **Add photos** (drag-and-drop or File > Add Photos)
2. **View metadata** by hovering over photos (tooltip preview)
3. **Select/load a template** or edit from scratch
4. **Apply metadata** to all photos at once
5. **Delete metadata** from all photos at once
6. **Batch rename** photos with a pattern
7. **Save/update templates** for reuse

## App Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Templates  Help                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Photo Queue     Metadata Editor          Batch Actions          │
│ ┌──────────────┐ ┌──────────────────────┐ ┌─────────────────┐   │
│ │ IMG001.jpg   │ │ Template: <dropdown> │ │ Apply Metadata  │   │
│ │ IMG002.jpg   │ │ [New]                │ │ to All Photos   │   │
│ │ IMG003.jpg   │ │                      │ │                 │   │
│ │              │ │ Title: _______       │ │ Delete All      │   │
│ │ (hover for   │ │ Subject: _______     │ │ Metadata        │   │
│ │  metadata)   │ │ Tags: _______        │ │                 │   │
│ │              │ │ Comments: ______     │ │ Batch Rename    │   │
│ │ [Remove Sel] │ │ Authors: _______     │ │ Photos          │   │
│ │              │ │ Copyright: _______   │ │                 │   │
│ └──────────────┘ └──────────────────────┘ │ Save as         │   │
│                                            │ Template        │   │
│                                            └─────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Examples

### Example 1: Apply same metadata to batch of photos
1. **Drag photos** into the "Photo Queue" (left panel)
2. **Hover over each** to see current metadata
3. **Edit metadata fields** (Title, Subject, Tags, Comments, Authors, Copyright)
4. Click **"Apply Metadata to All Photos"** button
5. All photos updated with new EXIF/XMP tags

### Example 2: Use a template
1. **Add photos** to queue
2. **Select template** from dropdown (e.g., "Civil Air Patrol")
3. Editor auto-fills with template values
4. **Customize** any fields as needed
5. Click **"Apply Metadata to All Photos"**

### Example 3: Save a new template
1. **Edit metadata fields** with your preferred values
2. Click **"Save as Template"** button
3. **Enter template name** (e.g., "Event 2025")
4. Template saved and available in future sessions

### Example 4: Batch rename photos
1. **Select photos** in queue
2. Click **"Batch Rename Photos"** button
3. **Enter pattern**: e.g., `CAP_Training_{index}`
4. Set **start index** (e.g., 1) and **zero-padding** (e.g., 3 → 001, 002, ...)
5. Choose **case** (as-is, lower, upper, title)
6. **Preview** first 3 renames
7. Click OK → all photos renamed

### Example 5: Clean metadata from batch
1. **Add photos** to queue
2. Click **"Delete All Metadata"** button
3. **Confirm** the action
4. All EXIF/XMP metadata removed from all photos

## New Features

### Hover Tooltips on Photo Queue
- **Mouse over any photo** in the queue
- **Tooltip shows** up to 5 key metadata fields:
  - ImageDescription
  - Subject
  - Artist
  - Copyright
  - UserComment / XPKeywords
- Preview truncated to 60 chars per line

### Metadata Editor with Template Support
- **Template dropdown** at top of editor
- Click **"New"** to create template from current values
- Load template → editor auto-fills
- Edit → Click **"Save as Template"** to update/overwrite

### Batch Action Buttons (Right Panel)
1. **Apply Metadata to All Photos** - writes EXIF/XMP from editor
2. **Delete All Metadata** - removes all EXIF/XMP tags
3. **Batch Rename Photos** - rename with pattern and preview
4. **Save as Template** - save current editor values

## Behind the Scenes

### Metadata Reading (Normalized & Human-Readable)
All metadata is automatically:
- ✓ Decoded from UTF-16LE (XP fields), UTF-8, Latin-1
- ✓ Rational tuples converted to decimals (e.g., `[1, 60]` → `0.0167`)
- ✓ GPS coordinates converted to decimal degrees
- ✓ Split multi-value fields into lists (keywords, tags)
- ✓ Control characters and nulls stripped

Example output:
```json
"XPKeywords": ["Civil Air Patrol", "Kentucky Wing", "Heartland Composite Squadron"],
"ExposureTime": 0.01666667,
"UserComment": "Located at Wendall H. Ford Regional Training Center, Greenville, KY"
```

### Metadata Writing
When you click **"Apply Metadata to All Photos"**:
- Photo title, subject, tags, comments, authors, copyright are written to EXIF
- XMP tags also created/updated for compatibility
- Original photo backed up (if overwriting)

### Template System
Templates stored in `~/.photo_metadata_templates/` as JSON files:
```json
{
  "name": "Civil Air Patrol",
  "metadata": {
    "title": "Civil Air Patrol Event",
    "subject": "CAP Training",
    "tags": ["Civil Air Patrol", "Kentucky Wing"],
    "authors": "Melanie Gledhill",
    "copyright": "Copyright Civil Air Patrol"
  }
}
```

## Commands to Run

```bash
# Install dependencies (first time)
pip3 install -r requirements.txt

# Run the app
cd src
python3 main.py

# Or use the run.sh script
./run.sh
```

## Files Modified

- **src/main.py** - Complete redesign for batch workflow
- **src/metadata_handler.py** - Improved normalization (XP fields, rationals, GPS)
- **src/templates.py** - Already supports template CRUD
- **requirements.txt** - Dependencies (wxPython, piexif, python-xmp-toolkit)

## Next Steps (Optional Enhancements)

- [ ] Add **search/filter** for photo queue
- [ ] Show **thumbnail previews** in queue
- [ ] Add **undo/redo** for batch operations
- [ ] Export metadata to CSV for batch import
- [ ] Support **more metadata fields** (location, rating, keywords arrays)
- [ ] Add **keyboard shortcuts** (e.g., Ctrl+A to select all)
- [ ] Implement **progress bar** for large batches

---

**Created**: November 11, 2025
**Version**: 2.0 - Batch Workflow Edition
