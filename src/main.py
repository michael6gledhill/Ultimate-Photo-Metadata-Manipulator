"""
Main GUI Application for Photo Metadata Manipulator
Built with wxPython
Batch metadata editor with template support.
"""

import wx
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from metadata_handler import MetadataHandler
from templates import TemplateManager


class MainFrame(wx.Frame):
    """Main application window for batch photo metadata editing."""

    def __init__(self):
        super().__init__(None, title="Photo Metadata Manipulator - Batch Editor", size=(1400, 800))

        self.metadata_handler = MetadataHandler()
        self.template_manager = TemplateManager()
        
        # Queue of files to process
        self.file_queue: List[str] = []
        
        # Current metadata being edited (will be applied to all files in queue)
        self.current_metadata_edits: Dict[str, Any] = {
            'title': '',
            'subject': '',
            'tags': [],
            'comments': '',
            'authors': '',
            'copyright': ''
        }
        
        # Current template (if loaded)
        self.current_template: Optional[str] = None

        self.init_ui()
        # Ensure layout is calculated before showing
        self.Layout()
        self.Centre()
        self.Show()

        # After show, schedule a final layout/refresh and a size event to force painting
        wx.CallAfter(self._finalize_layout)

    def init_ui(self):
        """Initialize the UI with file queue, editor, and batch controls."""
        main_panel = wx.Panel(self)
        # keep reference for final layout/refresh step
        self.main_panel = main_panel
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Menu Bar
        self.create_menu_bar()

        # LEFT PANEL: File Queue with drag-and-drop
        left_panel = self.create_file_queue_panel(main_panel)
        main_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)

        # CENTER PANEL: Template selector + Metadata editor
        center_panel = self.create_editor_panel(main_panel)
        main_sizer.Add(center_panel, 1, wx.EXPAND | wx.ALL, 5)

        # RIGHT PANEL: Batch action buttons
        right_panel = self.create_action_panel(main_panel)
        main_sizer.Add(right_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready. Drag photos here or use File > Add Photos.")

        main_panel.SetSizer(main_sizer)

    def _finalize_layout(self):
        """Finalize layout and force repaint after the frame is shown.

        This helps on some platforms where initial paint doesn't occur until a resize.
        """
        try:
            # Layout top-level frame and the main panel and its children
            self.Layout()
            try:
                self.main_panel.Layout()
                self.main_panel.Refresh()
            except Exception:
                pass
            for child in self.GetChildren():
                try:
                    child.Layout()
                    child.Refresh()
                except Exception:
                    pass
            # Force a repaint and send a synthetic size event
            self.Refresh()
            self.Update()
            try:
                # Some wx versions/platforms respond to SendSizeEvent
                self.SendSizeEvent()
            except Exception:
                pass
        except Exception as e:
            # If something goes wrong, print to stderr for debugging
            print("_finalize_layout error:", e)

    def create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "Add Photos\tCtrl+O")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Exit\tCtrl+Q")

        # Templates menu
        templates_menu = wx.Menu()
        templates_menu.Append(wx.ID_ANY, "New Template")
        templates_menu.Append(wx.ID_ANY, "Manage Templates")
        templates_menu.AppendSeparator()
        templates_menu.Append(wx.ID_ANY, "Load Template")

        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "About")

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(templates_menu, "&Templates")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind events
        self.Bind(wx.EVT_MENU, self.on_add_photos, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)

    def create_file_queue_panel(self, parent) -> wx.Panel:
        """Create left panel with file queue list and drag-and-drop."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        label = wx.StaticText(panel, label="Photo Queue")
        font = label.GetFont()
        font.PointSize += 2
        font = font.Bold()
        label.SetFont(font)

        # File list with drag-and-drop
        self.file_list = wx.ListBox(panel, size=(250, 600))
        self.file_list.Bind(wx.EVT_LISTBOX, self.on_file_selected)
        self.file_list.Bind(wx.EVT_MOTION, self.on_file_list_motion)

        # Enable drag-and-drop
        class FileDropTarget(wx.FileDropTarget):
            def __init__(self, target_widget, frame):
                super().__init__()
                self.target = target_widget
                self.frame = frame

            def OnDropFiles(self, x, y, filenames: List[str]) -> bool:
                for f in filenames:
                    if self.frame.metadata_handler.is_supported(f):
                        if self.target.FindString(f) == wx.NOT_FOUND:
                            self.target.Append(f)
                            self.frame.file_queue.append(f)
                
                if len(self.frame.file_queue) > 0:
                    self.frame.SetStatusText(f"Loaded {len(self.frame.file_queue)} photo(s)")
                return True

        self.file_list.SetDropTarget(FileDropTarget(self.file_list, self))

        # Remove button
        btn_remove = wx.Button(panel, label="Remove Selected")
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove_photo)

        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_remove, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        panel.Layout()
        return panel

    def create_editor_panel(self, parent) -> wx.Panel:
        """Create center panel with metadata editor."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Template selector at top
        template_sizer = wx.BoxSizer(wx.HORIZONTAL)
        template_sizer.Add(wx.StaticText(panel, label="Template:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.template_choice = wx.Choice(panel, choices=self.get_template_list())
        self.template_choice.SetSelection(0)
        self.template_choice.Bind(wx.EVT_CHOICE, self.on_template_selected)
        template_sizer.Add(self.template_choice, 1, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(template_sizer, 0, wx.EXPAND)

        # Metadata editor fields
        editor_label = wx.StaticText(panel, label="Metadata Editor")
        font = editor_label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        editor_label.SetFont(font)

        sizer.Add(editor_label, 0, wx.ALL, 5)

        grid = wx.FlexGridSizer(6, 2, 8, 8)
        grid.AddGrowableCol(1, 1)

        self.tc_title = wx.TextCtrl(panel)
        self.tc_subject = wx.TextCtrl(panel)
        self.tc_tags = wx.TextCtrl(panel)
        self.tc_comments = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(-1, 60))
        self.tc_authors = wx.TextCtrl(panel)
        self.tc_copyright = wx.TextCtrl(panel)

        grid.Add(wx.StaticText(panel, label="Title:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_title, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Subject:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_subject, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Tags (comma-separated):"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_tags, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Comments:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_comments, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Authors (semicolon-separated):"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_authors, 1, wx.EXPAND)
        grid.Add(wx.StaticText(panel, label="Copyright:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tc_copyright, 1, wx.EXPAND)

        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)

        # Thumbnail preview
        thumb_label = wx.StaticText(panel, label="Preview")
        sizer.Add(thumb_label, 0, wx.LEFT | wx.TOP, 6)
        self.preview_bitmap = wx.StaticBitmap(panel, bitmap=wx.NullBitmap, size=(320, 240))
        sizer.Add(self.preview_bitmap, 0, wx.ALL, 5)

        panel.SetSizer(sizer)
        panel.Layout()
        return panel

    def create_action_panel(self, parent) -> wx.Panel:
        """Create right panel with batch action buttons."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Batch Actions Section
        batch_label = wx.StaticText(panel, label="Batch Actions")
        font = batch_label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        batch_label.SetFont(font)
        sizer.Add(batch_label, 0, wx.ALL, 5)

        # Buttons
        btn_apply = wx.Button(panel, label="Apply Metadata\nto All Photos", size=(140, 60))
        btn_apply.Bind(wx.EVT_BUTTON, self.on_apply_metadata)
        sizer.Add(btn_apply, 0, wx.EXPAND | wx.ALL, 5)

        btn_delete = wx.Button(panel, label="Delete All\nMetadata", size=(140, 60))
        btn_delete.Bind(wx.EVT_BUTTON, self.on_delete_all_metadata)
        sizer.Add(btn_delete, 0, wx.EXPAND | wx.ALL, 5)

        btn_rename = wx.Button(panel, label="Batch Rename\nPhotos", size=(140, 60))
        btn_rename.Bind(wx.EVT_BUTTON, self.on_batch_rename)
        sizer.Add(btn_rename, 0, wx.EXPAND | wx.ALL, 5)

        # Single Photo Actions Section
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 8)
        
        single_label = wx.StaticText(panel, label="Single Photo Actions")
        font = single_label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        single_label.SetFont(font)
        sizer.Add(single_label, 0, wx.ALL, 5)

        btn_apply_sel = wx.Button(panel, label="Apply to\nSelected", size=(140, 60))
        btn_apply_sel.Bind(wx.EVT_BUTTON, self.on_apply_metadata_selected)
        sizer.Add(btn_apply_sel, 0, wx.EXPAND | wx.ALL, 5)

        btn_clear_sel = wx.Button(panel, label="Clear Metadata\nfrom Selected", size=(140, 60))
        btn_clear_sel.Bind(wx.EVT_BUTTON, self.on_clear_metadata_selected)
        sizer.Add(btn_clear_sel, 0, wx.EXPAND | wx.ALL, 5)

        # Template Management Section
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 8)
        
        template_label = wx.StaticText(panel, label="Templates")
        font = template_label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        template_label.SetFont(font)
        sizer.Add(template_label, 0, wx.ALL, 5)

        # Template management buttons
        btn_save_template = wx.Button(panel, label="Save As New\nTemplate", size=(140, 50))
        btn_save_template.Bind(wx.EVT_BUTTON, self.on_save_as_template)
        sizer.Add(btn_save_template, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_update_template = wx.Button(panel, label="Update Selected\nTemplate", size=(140, 50))
        btn_update_template.Bind(wx.EVT_BUTTON, self.on_update_template)
        sizer.Add(btn_update_template, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_delete_template = wx.Button(panel, label="Delete Selected\nTemplate", size=(140, 50))
        btn_delete_template.Bind(wx.EVT_BUTTON, self.on_delete_template)
        sizer.Add(btn_delete_template, 0, wx.EXPAND | wx.ALL, 5)

        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        panel.Layout()
        return panel

    def get_template_list(self) -> List[str]:
        """Get list of available templates plus '<None>' option."""
        templates = self.template_manager.list_templates()
        return ['<No Template>'] + templates

    def on_add_photos(self, event):
        """Open file dialog to add photos to queue."""
        wildcard = "Image files (*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.gif;*.bmp)|*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.gif;*.bmp|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Add Photos", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for p in paths:
                if p not in self.file_queue:
                    self.file_list.Append(p)
                    self.file_queue.append(p)
            self.SetStatusText(f"Loaded {len(self.file_queue)} photo(s)")

        dlg.Destroy()

    def on_remove_photo(self, event):
        """Remove selected photo from queue."""
        sel = self.file_list.GetSelection()
        if sel != wx.NOT_FOUND:
            self.file_list.Delete(sel)
            del self.file_queue[sel]
            self.SetStatusText(f"{len(self.file_queue)} photo(s) in queue")

    def on_file_selected(self, event):
        """Handle file selection in queue (show metadata preview)."""
        sel = self.file_list.GetSelection()
        if sel != wx.NOT_FOUND:
            file_path = self.file_queue[sel]
            self.show_metadata_preview(file_path)

    def on_file_list_motion(self, event):
        """Show tooltip with metadata preview when hovering over file list."""
        pos = event.GetPosition()
        idx = self.file_list.HitTest(pos)
        
        if idx != wx.NOT_FOUND:
            file_path = self.file_queue[idx]
            # Read metadata
            metadata = self.metadata_handler.read_metadata(file_path)
            
            if metadata and metadata.get('exif'):
                exif = metadata['exif']
                preview_lines = []
                
                # Build preview from key fields
                key_fields = ['ImageDescription', 'Subject', 'Artist', 'Copyright', 'UserComment', 'XPKeywords']
                for key in key_fields:
                    val = exif.get(key)
                    if val:
                        if isinstance(val, list):
                            val_str = '; '.join(str(v) for v in val)
                        else:
                            val_str = str(val)
                        if len(val_str) > 60:
                            val_str = val_str[:57] + '...'
                        preview_lines.append(f"{key}: {val_str}")
                
                if preview_lines:
                    tooltip = '\n'.join(preview_lines[:5])  # Show first 5 fields
                    self.file_list.SetToolTip(tooltip)
                    return
        
        self.file_list.SetToolTip("")

    def show_metadata_preview(self, file_path: str):
        """Show metadata preview for a specific file and populate editor with current metadata."""
        metadata = self.metadata_handler.read_metadata(file_path)
        if not metadata:
            return
        
        # Could display in a status bar or dialog
        exif = metadata.get('exif', {})
        xmp = metadata.get('xmp', {})
        self.SetStatusText(f"File: {Path(file_path).name} | EXIF fields: {len(exif)}")
        
        # Auto-populate editor fields with current metadata from file
        # Priority: EXIF > XMP > empty
        title = exif.get('ImageDescription', '') or xmp.get('title', '')
        subject = exif.get('XPSubject', '') or xmp.get('subject', '')
        # Tags: try XPKeywords (EXIF) first, then dc:subject from XMP
        tags_val = exif.get('XPKeywords', []) or xmp.get('subject', [])
        if isinstance(tags_val, list):
            tags_str = ', '.join(str(t) for t in tags_val)
        else:
            tags_str = str(tags_val) if tags_val else ''
        
        comments = exif.get('UserComment', '') or xmp.get('description', '')
        authors = exif.get('Artist', '') or xmp.get('creator', '')
        if isinstance(authors, list):
            authors = '; '.join(str(a) for a in authors)
        copyright_val = exif.get('Copyright', '') or xmp.get('rights', '')
        
        # Populate editor with loaded metadata (but don't override if user typed something)
        # Actually: always load from file to let user see and edit what's currently in the file
        self.tc_title.SetValue(str(title).strip() if title else '')
        self.tc_subject.SetValue(str(subject).strip() if subject else '')
        self.tc_tags.SetValue(tags_str.strip() if tags_str else '')
        self.tc_comments.SetValue(str(comments).strip() if comments else '')
        self.tc_authors.SetValue(str(authors).strip() if authors else '')
        self.tc_copyright.SetValue(str(copyright_val).strip() if copyright_val else '')
        
        # Update thumbnail preview (scaled)
        try:
            img = wx.Image(file_path)
            iw, ih = img.GetSize()
            maxw, maxh = 320, 240
            scale = min(maxw / iw, maxh / ih, 1.0)
            nw, nh = int(iw * scale), int(ih * scale)
            img = img.Scale(nw, nh, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img)
            self.preview_bitmap.SetBitmap(bmp)
        except Exception:
            # clear bitmap on failure
            try:
                self.preview_bitmap.SetBitmap(wx.NullBitmap)
            except Exception:
                pass

    def on_template_selected(self, event):
        """Load selected template into editor."""
        sel = self.template_choice.GetSelection()
        if sel <= 0:  # '<No Template>' or nothing
            self.current_template = None
            return
        
        template_name = self.template_choice.GetString(sel)
        template_data = self.template_manager.load_template(template_name)
        
        if template_data:
            self.current_template = template_name
            # Populate editor with template values
            metadata = template_data.get('metadata', {})
            self.tc_title.SetValue(metadata.get('title', ''))
            self.tc_subject.SetValue(metadata.get('subject', ''))
            self.tc_tags.SetValue(','.join(metadata.get('tags', [])))
            self.tc_comments.SetValue(metadata.get('comments', ''))
            self.tc_authors.SetValue(metadata.get('authors', ''))
            self.tc_copyright.SetValue(metadata.get('copyright', ''))
            
            self.SetStatusText(f"Loaded template: {template_name}")

    def on_save_as_template(self, event):
        """Save current editor values as a new template with a new name."""
        dlg = wx.TextEntryDialog(self, "Enter new template name:")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                metadata = self.collect_editor_metadata()
                self.template_manager.create_template(name, metadata, f"Template: {name}")
                
                # Refresh template list
                self.template_choice.Clear()
                for t in self.get_template_list():
                    self.template_choice.Append(t)
                
                # Select the newly created template
                idx = self.template_choice.FindString(name)
                if idx != wx.NOT_FOUND:
                    self.template_choice.SetSelection(idx)
                    self.current_template = name
                
                wx.MessageBox(f"Template '{name}' created.", "Success", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_new_template(self, event):
        """Create a new template from current editor values."""
        dlg = wx.TextEntryDialog(self, "Enter new template name:")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                metadata = self.collect_editor_metadata()
                self.template_manager.create_template(name, metadata, f"Template: {name}")
                
                # Refresh template list
                self.template_choice.Clear()
                for t in self.get_template_list():
                    self.template_choice.Append(t)
                
                # Select the newly created template
                idx = self.template_choice.FindString(name)
                if idx != wx.NOT_FOUND:
                    self.template_choice.SetSelection(idx)
                    self.current_template = name
                
                wx.MessageBox(f"Template '{name}' created.", "Success", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_save_as_template(self, event):
        """Save current editor values as a new template with a new name."""
        dlg = wx.TextEntryDialog(self, "Enter new template name:")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                metadata = self.collect_editor_metadata()
                self.template_manager.create_template(name, metadata, f"Template: {name}")
                
                # Refresh template list
                self.template_choice.Clear()
                for t in self.get_template_list():
                    self.template_choice.Append(t)
                
                # Select the newly created template
                idx = self.template_choice.FindString(name)
                if idx != wx.NOT_FOUND:
                    self.template_choice.SetSelection(idx)
                    self.current_template = name
                
                wx.MessageBox(f"Template '{name}' created.", "Success", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_update_template(self, event):
        """Update the selected template with current editor values."""
        sel = self.template_choice.GetSelection()
        if sel <= 0:  # '<No Template>' or nothing selected
            wx.MessageBox("Please select a template to update.", "No Template Selected", wx.OK | wx.ICON_WARNING)
            return
        
        template_name = self.template_choice.GetString(sel)
        
        # Collect current editor metadata
        metadata = self.collect_editor_metadata()
        
        # Confirm update
        dlg = wx.MessageDialog(
            self,
            f"Update template '{template_name}' with current editor values?",
            "Confirm Update",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            template_data = {
                'name': template_name,
                'description': f"Updated template: {template_name}",
                'metadata': metadata
            }
            self.template_manager.templates[template_name] = template_data
            self.template_manager.save_template(template_name, template_data)
            self.current_template = template_name
            wx.MessageBox(f"Template '{template_name}' updated.", "Success", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()

    def on_delete_template(self, event):
        """Delete the selected template."""
        sel = self.template_choice.GetSelection()
        if sel <= 0:  # '<No Template>' or nothing selected
            wx.MessageBox("Please select a template to delete.", "No Template Selected", wx.OK | wx.ICON_WARNING)
            return
        
        template_name = self.template_choice.GetString(sel)
        
        # Confirm deletion
        dlg = wx.MessageDialog(
            self,
            f"Delete template '{template_name}'?\n\nThis cannot be undone.",
            "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            try:
                self.template_manager.delete_template(template_name)
                
                # Refresh template list
                self.template_choice.Clear()
                for t in self.get_template_list():
                    self.template_choice.Append(t)
                self.template_choice.SetSelection(0)
                self.current_template = None
                
                wx.MessageBox(f"Template '{template_name}' deleted.", "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Error deleting template: {e}", "Error", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()

    def on_manage_templates(self, event):
        """Open template manager dialog to delete or manage templates."""
        dlg = TemplateManagerDialog(self, self.template_manager)
        if dlg.ShowModal() == wx.ID_OK:
            # Refresh template list after management
            self.template_choice.Clear()
            for t in self.get_template_list():
                self.template_choice.Append(t)
            self.template_choice.SetSelection(0)
            self.current_template = None
        dlg.Destroy()

    def collect_editor_metadata(self) -> Dict[str, Any]:
        """Collect metadata from editor fields."""
        return {
            'title': self.tc_title.GetValue().strip(),
            'subject': self.tc_subject.GetValue().strip(),
            'tags': [t.strip() for t in self.tc_tags.GetValue().split(',') if t.strip()],
            'comments': self.tc_comments.GetValue().strip(),
            'authors': self.tc_authors.GetValue().strip(),
            'copyright': self.tc_copyright.GetValue().strip()
        }

    def on_apply_metadata(self, event):
        """Apply current editor metadata to all photos in queue."""
        if not self.file_queue:
            wx.MessageBox("No photos in queue.", "Error", wx.OK | wx.ICON_WARNING)
            return

        metadata = self.collect_editor_metadata()

        dlg = wx.MessageDialog(self,
                               f"Apply metadata to {len(self.file_queue)} photo(s)?\n\nThis will update EXIF and XMP.",
                               "Confirm",
                               wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()

        total = len(self.file_queue)
        prog = wx.ProgressDialog("Applying metadata",
                                 f"Applying metadata to {total} photos...",
                                 maximum=total,
                                 parent=self,
                                 style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

        applied = 0
        failed: List[str] = []

        for idx, file_path in enumerate(list(self.file_queue), start=1):
            wx.YieldIfNeeded()
            ok = self.metadata_handler.edit_metadata(file_path, metadata, None)
            if ok:
                applied += 1
            else:
                failed.append(Path(file_path).name)

            keep_going = prog.Update(idx)[0]
            if not keep_going:
                # user cancelled
                break

        prog.Destroy()
        summary = f"Applied metadata to {applied}/{total} photos."
        if failed:
            summary += f" Failed: {', '.join(failed)}"

        self.SetStatusText(summary)

    def on_apply_metadata_selected(self, event):
        """Apply current editor metadata to the currently selected photo only."""
        sel = self.file_list.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageBox("No photo selected.", "Error", wx.OK | wx.ICON_WARNING)
            return

        file_path = self.file_queue[sel]
        metadata = self.collect_editor_metadata()

        dlg = wx.MessageDialog(self,
                               f"Apply metadata to selected photo:\n{Path(file_path).name}?",
                               "Confirm",
                               wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()

        prog = wx.ProgressDialog("Applying metadata",
                                 f"Applying metadata to {Path(file_path).name}...",
                                 maximum=1,
                                 parent=self,
                                 style=wx.PD_ELAPSED_TIME)
        ok = self.metadata_handler.edit_metadata(file_path, metadata, None)
        prog.Update(1)
        prog.Destroy()

        if ok:
            self.SetStatusText(f"Applied metadata to {Path(file_path).name}")
        else:
            self.SetStatusText(f"Failed to apply metadata to {Path(file_path).name}")

    def on_clear_metadata_selected(self, event):
        """Clear all metadata from the currently selected photo only."""
        sel = self.file_list.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageBox("No photo selected.", "Error", wx.OK | wx.ICON_WARNING)
            return

        file_path = self.file_queue[sel]

        dlg = wx.MessageDialog(self,
                               f"Clear all metadata from selected photo:\n{Path(file_path).name}?\n\nThis cannot be undone.",
                               "Confirm",
                               wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()

        prog = wx.ProgressDialog("Clearing metadata",
                                 f"Removing metadata from {Path(file_path).name}...",
                                 maximum=1,
                                 parent=self,
                                 style=wx.PD_ELAPSED_TIME)
        ok = self.metadata_handler.delete_all_metadata(file_path, file_path)
        prog.Update(1)
        prog.Destroy()

        if ok:
            self.SetStatusText(f"Cleared metadata from {Path(file_path).name}")
            # Refresh the preview to show cleared metadata
            self.show_metadata_preview(file_path)
        else:
            self.SetStatusText(f"Failed to clear metadata from {Path(file_path).name}")

    def on_delete_all_metadata(self, event):
        """Delete all metadata from photos in queue."""
        if not self.file_queue:
            wx.MessageBox("No photos in queue.", "Error", wx.OK | wx.ICON_WARNING)
            return
        dlg = wx.MessageDialog(self,
                               f"Delete all metadata from {len(self.file_queue)} photo(s)?\n\nThis cannot be undone.",
                               "Confirm",
                               wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()

        total = len(self.file_queue)
        prog = wx.ProgressDialog("Deleting metadata",
                                 f"Removing metadata from {total} photos...",
                                 maximum=total,
                                 parent=self,
                                 style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

        deleted = 0
        failed: List[str] = []

        for idx, file_path in enumerate(list(self.file_queue), start=1):
            wx.YieldIfNeeded()
            ok = self.metadata_handler.delete_all_metadata(file_path, file_path)
            if ok:
                deleted += 1
            else:
                failed.append(Path(file_path).name)

            keep_going = prog.Update(idx)[0]
            if not keep_going:
                break

        prog.Destroy()
        summary = f"Deleted metadata from {deleted}/{total} photos."
        if failed:
            summary += f" Failed: {', '.join(failed)}"
        self.SetStatusText(summary)

    def on_batch_rename(self, event):
        """Open batch rename dialog."""
        if not self.file_queue:
            wx.MessageBox("No photos in queue.", "Error", wx.OK | wx.ICON_WARNING)
            return
        
        dlg = BatchRenameDialog(self, self.file_queue)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        """Exit the application."""
        self.Close(True)


class BatchRenameDialog(wx.Dialog):
    """Dialog to batch rename files using a pattern with {index}."""

    def __init__(self, parent, file_list: List[str]):
        super().__init__(parent, title="Batch Rename", size=(650, 480))
        self.file_list = file_list
        self.parent_frame = parent
        self.mode_controls = {}  # Track controls by mode
        self.init_ui()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Mode choice: Pattern or other operations
        mode_h = wx.BoxSizer(wx.HORIZONTAL)
        mode_h.Add(wx.StaticText(self, label="Mode:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        self.choice_mode = wx.Choice(self, choices=["Pattern (with {index})", "Prefix", "Suffix", "Find & Replace", "Increment"])
        self.choice_mode.SetSelection(0)
        self.choice_mode.Bind(wx.EVT_CHOICE, self.on_mode_changed)
        mode_h.Add(self.choice_mode, 1, wx.EXPAND | wx.ALL, 6)
        sizer.Add(mode_h, 0, wx.LEFT | wx.EXPAND)

        # Pattern and options (7 rows x 2 cols)
        grid = wx.FlexGridSizer(7, 2, 8, 8)
        grid.AddGrowableCol(1, 1)
        
        grid.Add(wx.StaticText(self, label="Pattern (use {index}):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_pattern = wx.TextCtrl(self, value="photo_{index}")
        self.tc_pattern.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        grid.Add(self.tc_pattern, 1, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Prefix:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_prefix = wx.TextCtrl(self, value="")
        self.tc_prefix.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        grid.Add(self.tc_prefix, 1, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Suffix:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_suffix = wx.TextCtrl(self, value="")
        self.tc_suffix.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        grid.Add(self.tc_suffix, 1, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Find (search):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_find = wx.TextCtrl(self, value="")
        self.tc_find.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        grid.Add(self.tc_find, 1, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Replace with:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_replace = wx.TextCtrl(self, value="")
        self.tc_replace.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        grid.Add(self.tc_replace, 1, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Start index:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_start = wx.SpinCtrl(self, value="1", min=0, max=1000000)
        self.spin_start.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        grid.Add(self.spin_start, 0, wx.EXPAND)
        
        grid.Add(wx.StaticText(self, label="Zero-pad width:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_pad = wx.SpinCtrl(self, value="0", min=0, max=10)
        self.spin_pad.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        grid.Add(self.spin_pad, 0, wx.EXPAND)

        sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 8)

        # Case choice
        case_h = wx.BoxSizer(wx.HORIZONTAL)
        case_h.Add(wx.StaticText(self, label="Case:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        self.choice_case = wx.Choice(self, choices=["as-is", "lower", "upper", "title"])
        self.choice_case.SetSelection(0)
        self.choice_case.Bind(wx.EVT_CHOICE, lambda e: self.update_preview())
        case_h.Add(self.choice_case, 0, wx.ALL, 6)
        sizer.Add(case_h, 0, wx.LEFT)

        # Preview of first 3 renamed files
        sizer.Add(wx.StaticText(self, label="Preview (first 3):"), 0, wx.LEFT | wx.TOP, 6)
        self.tc_preview = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 150))
        sizer.Add(self.tc_preview, 1, wx.EXPAND | wx.ALL, 8)

        # Bind events to update preview when options change
        self.tc_pattern.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        self.spin_start.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        self.spin_pad.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        self.choice_case.Bind(wx.EVT_CHOICE, lambda e: self.update_preview())

        # Buttons: Rename All or Cancel
        btn_h = wx.BoxSizer(wx.HORIZONTAL)
        btn_h.AddStretchSpacer()
        
        btn_rename_all = wx.Button(self, wx.ID_OK, "Rename All Now")
        btn_rename_all.Bind(wx.EVT_BUTTON, self.on_rename_all)
        btn_h.Add(btn_rename_all, 0, wx.ALL, 5)
        
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        btn_h.Add(cancel_button, 0, wx.ALL, 5)
        
        sizer.Add(btn_h, 0, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(sizer)
        # initial preview
        self.update_preview()

    def on_mode_changed(self, event):
        """Handle mode change to show/hide relevant fields."""
        mode = self.choice_mode.GetString(self.choice_mode.GetSelection())
        
        # Disable/enable fields based on mode
        self.tc_pattern.Enable(mode == "Pattern (with {index})")
        self.tc_prefix.Enable(mode == "Prefix")
        self.tc_suffix.Enable(mode == "Suffix")
        self.tc_find.Enable(mode == "Find & Replace")
        self.tc_replace.Enable(mode == "Find & Replace")
        
        # Always enable start index and pad for modes that use numbering
        use_numbering = mode in ["Pattern (with {index})", "Increment"]
        self.spin_start.Enable(use_numbering)
        self.spin_pad.Enable(use_numbering)
        
        self.update_preview()

    def get_values(self):
        return (self.tc_pattern.GetValue(), int(self.spin_start.GetValue()), int(self.spin_pad.GetValue()), self.choice_case.GetString(self.choice_case.GetSelection()))

    def update_preview(self):
        """Update the preview box showing the first three target names."""
        mode = self.choice_mode.GetString(self.choice_mode.GetSelection())
        case = self.choice_case.GetString(self.choice_case.GetSelection())
        
        # Build preview mapping for the files in the provided list (show up to 500 entries)
        lines = []
        limit = min(len(self.file_list), 3)  # Show only first 3 for preview
        
        for i in range(limit):
            orig = Path(self.file_list[i])
            new_base = orig.stem  # filename without extension
            
            if mode == "Pattern (with {index})":
                pattern = self.tc_pattern.GetValue()
                try:
                    start = int(self.spin_start.GetValue())
                except Exception:
                    start = 1
                try:
                    pad = int(self.spin_pad.GetValue())
                except Exception:
                    pad = 0
                idx = start + i
                index_str = str(idx).zfill(pad)
                new_base = pattern.replace('{index}', index_str)
            
            elif mode == "Prefix":
                prefix = self.tc_prefix.GetValue()
                new_base = prefix + new_base
            
            elif mode == "Suffix":
                suffix = self.tc_suffix.GetValue()
                new_base = new_base + suffix
            
            elif mode == "Find & Replace":
                find_str = self.tc_find.GetValue()
                replace_str = self.tc_replace.GetValue()
                new_base = new_base.replace(find_str, replace_str)
            
            elif mode == "Increment":
                # Just add number to filename
                try:
                    start = int(self.spin_start.GetValue())
                except Exception:
                    start = 1
                try:
                    pad = int(self.spin_pad.GetValue())
                except Exception:
                    pad = 0
                idx = start + i
                index_str = str(idx).zfill(pad)
                new_base = new_base + "_" + index_str
            
            # Apply case transformation
            if case == 'lower':
                new_base = new_base.lower()
            elif case == 'upper':
                new_base = new_base.upper()
            elif case == 'title':
                new_base = new_base.title()
            
            new_name = f"{new_base}{orig.suffix}"
            lines.append(f"{orig.name} -> {new_name}")
        
        if len(self.file_list) > limit:
            lines.append(f"... and {len(self.file_list)-limit} more ...")
        
        self.tc_preview.SetValue('\n'.join(lines))

    def on_rename_all(self, event):
        """Execute batch rename now and close dialog."""
        mode = self.choice_mode.GetString(self.choice_mode.GetSelection())
        case = self.choice_case.GetString(self.choice_case.GetSelection())
        
        try:
            start = int(self.spin_start.GetValue())
        except Exception:
            start = 1
        try:
            padding = int(self.spin_pad.GetValue())
        except Exception:
            padding = 0

        total = len(self.file_list)
        prog = wx.ProgressDialog("Renaming files",
                                 f"Renaming {total} files...",
                                 maximum=total,
                                 parent=self,
                                 style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

        renamed = 0
        failed = []

        # iterate by index so we can update the queue/list in-place
        for i in range(len(self.file_list)):
            old_path = Path(self.file_list[i])
            new_base = old_path.stem  # filename without extension
            
            # Apply rename mode
            if mode == "Pattern (with {index})":
                pattern = self.tc_pattern.GetValue()
                idx = start + i
                index_str = str(idx).zfill(padding)
                new_base = pattern.replace('{index}', index_str)
            
            elif mode == "Prefix":
                prefix = self.tc_prefix.GetValue()
                new_base = prefix + new_base
            
            elif mode == "Suffix":
                suffix = self.tc_suffix.GetValue()
                new_base = new_base + suffix
            
            elif mode == "Find & Replace":
                find_str = self.tc_find.GetValue()
                replace_str = self.tc_replace.GetValue()
                new_base = new_base.replace(find_str, replace_str)
            
            elif mode == "Increment":
                idx = start + i
                index_str = str(idx).zfill(padding)
                new_base = new_base + "_" + index_str
            
            # Apply case transformation
            if case == 'lower':
                new_base = new_base.lower()
            elif case == 'upper':
                new_base = new_base.upper()
            elif case == 'title':
                new_base = new_base.title()

            new_path = old_path.with_name(f"{new_base}{old_path.suffix}")
            try:
                old_path.rename(new_path)
                # update internal queue and listbox in parent frame
                self.file_list[i] = str(new_path)
                try:
                    self.parent_frame.file_list.SetString(i, str(new_path))
                    self.parent_frame.file_queue[i] = str(new_path)
                except Exception:
                    pass
                renamed += 1
            except Exception:
                failed.append(old_path.name)

            keep_going = prog.Update(i + 1)[0]
            if not keep_going:
                break

        prog.Destroy()
        summary = f"Renamed {renamed}/{total} photos."
        if failed:
            summary += f" Failed: {', '.join(failed)}"
        self.parent_frame.SetStatusText(summary)
        
        # Close the dialog
        self.EndModal(wx.ID_OK)


class TemplateManagerDialog(wx.Dialog):
    """Dialog for managing saved templates."""

    def __init__(self, parent: wx.Frame, template_manager):
        """Initialize the dialog.
        
        Args:
            parent: Parent frame.
            template_manager: TemplateManager instance for CRUD operations.
        """
        super().__init__(parent, title="Manage Templates", size=(400, 300))
        self.template_manager = template_manager
        self.parent_frame = parent
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Saved Templates:")
        title_font = title.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL, 10)
        
        # Template list box
        self.lb_templates = wx.ListBox(panel)
        self.refresh_template_list()
        sizer.Add(self.lb_templates, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_delete = wx.Button(panel, label="Delete Selected")
        btn_delete.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_sizer.Add(btn_delete, 0, wx.RIGHT, 5)
        
        btn_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.Add(btn_close, 0)
        
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        panel.SetSizer(sizer)

    def refresh_template_list(self):
        """Refresh the template list box."""
        self.lb_templates.Clear()
        templates = self.template_manager.list_templates()
        for template_name in templates:
            self.lb_templates.Append(template_name)

    def on_delete(self, event):
        """Delete the selected template."""
        selection = self.lb_templates.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("Please select a template to delete.", "No Selection", wx.OK | wx.ICON_WARNING)
            return
        
        template_name = self.lb_templates.GetString(selection)
        dlg = wx.MessageDialog(
            self,
            f"Delete template '{template_name}'?",
            "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        if dlg.ShowModal() == wx.ID_YES:
            try:
                self.template_manager.delete_template(template_name)
                self.refresh_template_list()
                wx.MessageBox(f"Template '{template_name}' deleted.", "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Error deleting template: {e}", "Error", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_close(self, event):
        """Close the dialog."""
        self.EndModal(wx.ID_OK)


class App(wx.App):
    """Application class."""

    def OnInit(self):
        """Initialize the application."""
        self.frame = MainFrame()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
