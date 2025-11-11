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
        self.Centre()
        self.Show()

    def init_ui(self):
        """Initialize the UI with file queue, editor, and batch controls."""
        main_panel = wx.Panel(self)
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
        return panel

    def create_editor_panel(self, parent) -> wx.Panel:
        """Create center panel with template selector and metadata editor."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Template selector
        template_sizer = wx.BoxSizer(wx.HORIZONTAL)
        template_sizer.Add(wx.StaticText(panel, label="Template:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.template_choice = wx.Choice(panel, choices=self.get_template_list())
        self.template_choice.SetSelection(0)
        self.template_choice.Bind(wx.EVT_CHOICE, self.on_template_selected)
        template_sizer.Add(self.template_choice, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_new_template = wx.Button(panel, label="New")
        btn_new_template.Bind(wx.EVT_BUTTON, self.on_new_template)
        template_sizer.Add(btn_new_template, 0, wx.ALL, 5)
        
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

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

    def create_action_panel(self, parent) -> wx.Panel:
        """Create right panel with batch action buttons."""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="Batch Actions")
        font = label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        label.SetFont(font)
        sizer.Add(label, 0, wx.ALL, 5)

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

        sizer.AddStretchSpacer()

        # Template save
        btn_save_template = wx.Button(panel, label="Save as\nTemplate", size=(140, 50))
        btn_save_template.Bind(wx.EVT_BUTTON, self.on_save_template)
        sizer.Add(btn_save_template, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
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
        """Show metadata preview for a specific file (for debugging)."""
        metadata = self.metadata_handler.read_metadata(file_path)
        if not metadata:
            return
        
        # Could display in a status bar or dialog
        exif = metadata.get('exif', {})
        self.SetStatusText(f"File: {Path(file_path).name} | EXIF fields: {len(exif)}")

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
                self.template_choice.SetSelection(0)
                
                wx.MessageBox(f"Template '{name}' created.", "Success", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_save_template(self, event):
        """Save current editor values as template."""
        if self.current_template:
            # Update existing template
            metadata = self.collect_editor_metadata()
            self.template_manager.templates[self.current_template] = {
                'metadata': metadata,
                'description': f"Updated template: {self.current_template}"
            }
            self.template_manager.save_templates()
            wx.MessageBox(f"Template '{self.current_template}' updated.", "Success", wx.OK | wx.ICON_INFORMATION)
        else:
            self.on_new_template(event)

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
        
        if dlg.ShowModal() == wx.ID_YES:
            applied = 0
            failed = []
            
            for file_path in self.file_queue:
                if self.metadata_handler.edit_metadata(file_path, metadata, None):
                    applied += 1
                else:
                    failed.append(Path(file_path).name)
            
            msg = f"Applied metadata to {applied}/{len(self.file_queue)} photos."
            if failed:
                msg += f"\n\nFailed: {', '.join(failed)}"
            
            wx.MessageBox(msg, "Complete", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()

    def on_delete_all_metadata(self, event):
        """Delete all metadata from photos in queue."""
        if not self.file_queue:
            wx.MessageBox("No photos in queue.", "Error", wx.OK | wx.ICON_WARNING)
            return
        
        dlg = wx.MessageDialog(self,
                               f"Delete all metadata from {len(self.file_queue)} photo(s)?\n\nThis cannot be undone.",
                               "Confirm",
                               wx.YES_NO | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            deleted = 0
            failed = []
            
            for file_path in self.file_queue:
                if self.metadata_handler.delete_all_metadata(file_path, file_path):
                    deleted += 1
                else:
                    failed.append(Path(file_path).name)
            
            msg = f"Deleted metadata from {deleted}/{len(self.file_queue)} photos."
            if failed:
                msg += f"\n\nFailed: {', '.join(failed)}"
            
            wx.MessageBox(msg, "Complete", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()

    def on_batch_rename(self, event):
        """Open batch rename dialog."""
        if not self.file_queue:
            wx.MessageBox("No photos in queue.", "Error", wx.OK | wx.ICON_WARNING)
            return
        
        dlg = BatchRenameDialog(self, self.file_queue)
        if dlg.ShowModal() == wx.ID_OK:
            pattern, start, padding, case = dlg.get_values()
            
            renamed = 0
            failed = []
            
            for idx, file_path in enumerate(self.file_queue, start=start):
                p = Path(file_path)
                index_str = str(idx).zfill(padding)
                new_base = pattern.replace('{index}', index_str)
                
                if case == 'lower':
                    new_base = new_base.lower()
                elif case == 'upper':
                    new_base = new_base.upper()
                elif case == 'title':
                    new_base = new_base.title()
                
                new_path = p.with_name(f"{new_base}{p.suffix}")
                try:
                    p.rename(new_path)
                    renamed += 1
                except Exception as e:
                    failed.append(p.name)
            
            msg = f"Renamed {renamed}/{len(self.file_queue)} photos."
            if failed:
                msg += f"\n\nFailed: {', '.join(failed)}"
            
            wx.MessageBox(msg, "Complete", wx.OK | wx.ICON_INFORMATION)
        
        dlg.Destroy()

    def on_exit(self, event):
        """Exit the application."""
        self.Close(True)


class BatchRenameDialog(wx.Dialog):
    """Dialog to batch rename files using a pattern with {index}."""

    def __init__(self, parent, file_list: List[str]):
        super().__init__(parent, title="Batch Rename", size=(520, 240))
        self.file_list = file_list
        self.init_ui()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Pattern and options
        grid = wx.FlexGridSizer(3, 2, 8, 8)
        grid.Add(wx.StaticText(self, label="Pattern (use {index}):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.tc_pattern = wx.TextCtrl(self, value="photo_{index}")
        grid.Add(self.tc_pattern, 1, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Start index:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_start = wx.SpinCtrl(self, value="1", min=0, max=1000000)
        grid.Add(self.spin_start, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Zero-pad width:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.spin_pad = wx.SpinCtrl(self, value="0", min=0, max=10)
        grid.Add(self.spin_pad, 0, wx.EXPAND)

        sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 8)

        # Case choice
        case_h = wx.BoxSizer(wx.HORIZONTAL)
        case_h.Add(wx.StaticText(self, label="Case:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        self.choice_case = wx.Choice(self, choices=["as-is", "lower", "upper", "title"])
        self.choice_case.SetSelection(0)
        case_h.Add(self.choice_case, 0, wx.ALL, 6)
        sizer.Add(case_h, 0, wx.LEFT)

        # Preview of first 3 renamed files
        sizer.Add(wx.StaticText(self, label="Preview (first 3):"), 0, wx.LEFT | wx.TOP, 6)
        self.tc_preview = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 80))
        sizer.Add(self.tc_preview, 0, wx.EXPAND | wx.ALL, 8)

        # Bind events to update preview when options change
        self.tc_pattern.Bind(wx.EVT_TEXT, lambda e: self.update_preview())
        self.spin_start.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        self.spin_pad.Bind(wx.EVT_SPINCTRL, lambda e: self.update_preview())
        self.choice_case.Bind(wx.EVT_CHOICE, lambda e: self.update_preview())

        btn_sizer = wx.StdDialogButtonSizer()
        ok_button = wx.Button(self, wx.ID_OK)
        cancel_button = wx.Button(self, wx.ID_CANCEL)
        btn_sizer.AddButton(ok_button)
        btn_sizer.AddButton(cancel_button)
        btn_sizer.Realize()

        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 8)

        self.SetSizer(sizer)

        # initial preview
        self.update_preview()

    def get_values(self):
        return (self.tc_pattern.GetValue(), int(self.spin_start.GetValue()), int(self.spin_pad.GetValue()), self.choice_case.GetString(self.choice_case.GetSelection()))

    def update_preview(self):
        """Update the preview box showing the first three target names."""
        pattern = self.tc_pattern.GetValue()
        try:
            start = int(self.spin_start.GetValue())
        except Exception:
            start = 1
        try:
            pad = int(self.spin_pad.GetValue())
        except Exception:
            pad = 0
        case = self.choice_case.GetString(self.choice_case.GetSelection())

        # Preview first 3 files from the list
        lines = []
        for i in range(min(3, len(self.file_list))):
            idx = start + i
            index_str = str(idx).zfill(pad)
            new_base = pattern.replace('{index}', index_str)
            if case == 'lower':
                new_base = new_base.lower()
            elif case == 'upper':
                new_base = new_base.upper()
            elif case == 'title':
                new_base = new_base.title()
            
            # Show filename with extension from original
            orig_file = Path(self.file_list[i])
            lines.append(f"{new_base}{orig_file.suffix}")

        self.tc_preview.SetValue('\n'.join(lines))


class App(wx.App):
    """Application class."""

    def OnInit(self):
        """Initialize the application."""
        self.frame = MainFrame()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
