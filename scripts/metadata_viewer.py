#!/usr/bin/env python3
"""
Image Metadata Viewer (standalone)

A small, unrelated app that opens an image and displays ALL metadata (EXIF + XMP + general)
without depending on the main app. GUI built with Tkinter (no extra GUI deps).

Usage:
  python3 scripts/metadata_viewer.py [optional_image_path]

Features:
- Open image via file dialog or CLI argument
- Displays EXIF, XMP, and general info in a scrollable text area
- Copy All to clipboard
- Save as JSON next to the image

Requirements:
- Pillow
- piexif
- python-xmp-toolkit (optional; otherwise we try a fallback XMP extraction)
"""

import json
import os
import re
import sys
import binascii
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    # On macOS, make sure Python is a framework build if issues arise
    raise

from PIL import Image
import piexif

# Try to import libxmp (python-xmp-toolkit), otherwise we'll fallback
try:
    from libxmp import XMPFiles  # type: ignore
    HAVE_LIBXMP = True
except Exception:
    HAVE_LIBXMP = False


# -------------------- Metadata helpers --------------------

def _normalize_value(v: Any) -> Any:
    """Normalize metadata values for display/JSON."""
    # bytes -> attempt decodes
    if isinstance(v, (bytes, bytearray)):
        for enc in ("utf-8", "utf-16le", "utf-16be", "latin-1"):
            try:
                s = v.decode(enc)
                s = s.rstrip("\x00")
                s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]+", "", s)
                return s
            except Exception:
                continue
        try:
            return f"<bytes {len(v)} bytes: {binascii.hexlify(v[:16]).decode()}{'...' if len(v)>16 else ''}>"
        except Exception:
            return str(v)

    # dict -> normalize recursively
    if isinstance(v, dict):
        return {str(_normalize_value(k)): _normalize_value(val) for k, val in v.items()}

    # list/tuple -> handle rationals and byte arrays-as-ints
    if isinstance(v, (list, tuple)):
        if len(v) == 2 and all(isinstance(x, int) for x in v):
            num, den = v
            try:
                return round(num / den if den else 0, 8)
            except Exception:
                return [num, den]
        if len(v) > 0 and all(isinstance(x, int) and 0 <= x <= 255 for x in v):
            try:
                b = bytes(v)
                for enc in ("utf-16le", "utf-8", "latin-1"):
                    try:
                        s = b.decode(enc).rstrip("\x00")
                        parts = [p.strip() for p in re.split(r"[;,\x00]+", s) if p.strip()]
                        return parts if len(parts) > 1 else (parts[0] if parts else s)
                    except Exception:
                        continue
            except Exception:
                pass
        if len(v) > 0 and all(isinstance(x, (list, tuple)) and len(x) == 2 and all(isinstance(n, int) for n in x) for x in v):
            floats = []
            ok = True
            for num, den in v:
                try:
                    floats.append(num / den if den else 0)
                except Exception:
                    ok = False
                    break
            if ok:
                if len(floats) == 3:  # GPS DMS
                    deg, minute, sec = floats
                    try:
                        return deg + minute / 60.0 + sec / 3600.0
                    except Exception:
                        return floats
                return floats
        return [_normalize_value(x) for x in v]

    return v


def _normalize_metadata_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in d.items():
        key = k
        if isinstance(key, str) and '}' in key:
            key = key.split('}', 1)[1]
        out[str(key)] = _normalize_value(v)
    return out


def read_general(path: str) -> Dict[str, Any]:
    try:
        with Image.open(path) as img:
            return {
                "format": img.format,
                "size": img.size,
                "mode": img.mode,
                "file_size": os.path.getsize(path),
            }
    except Exception as e:
        return {"error": f"general: {e}"}


def read_exif(path: str) -> Dict[str, Any]:
    exif: Dict[str, Any] = {}
    try:
        data = piexif.load(path)
    except Exception as e:
        return {"error": f"exif: {e}"}

    for ifd_name, ifd in data.items():
        if not isinstance(ifd, dict):
            continue
        for tag, value in ifd.items():
            try:
                tag_info = piexif.TAGS.get(ifd_name, {}).get(tag)
                name = tag_info.get('name') if tag_info else None
            except Exception:
                name = None
            if not name:
                name = f"{ifd_name}:0x{tag:04X}"

            # XP* fields (UTF-16LE)
            try:
                if name.startswith('XP') or name.lower() in ('xpkeywords', 'xpsubject', 'xptitle', 'xpcomments'):
                    if isinstance(value, (list, tuple)):
                        try:
                            value = bytes(value)
                        except Exception:
                            value = str(value)
                    if isinstance(value, (bytes, bytearray)):
                        try:
                            s = value.decode('utf-16le', errors='ignore').rstrip('\x00')
                        except Exception:
                            s = value.decode('utf-8', errors='replace') if isinstance(value, (bytes, bytearray)) else str(value)
                        parts = [p.strip() for p in re.split(r'[;,\x00]+', s) if p.strip()]
                        value = parts if len(parts) > 1 else (parts[0] if parts else '')
                elif isinstance(value, (bytes, bytearray)):
                    try:
                        s = value.decode('utf-8', errors='replace')
                    except Exception:
                        try:
                            s = value.decode('utf-16le', errors='ignore')
                        except Exception:
                            s = str(value)
                    if name == 'UserComment' and s:
                        s = re.sub(r'^(ASCII|UNICODE|JIS)\s*\x00+', '', s, flags=re.IGNORECASE).rstrip('\x00').strip()
                    value = s
            except Exception:
                pass

            exif[name] = value

    try:
        return _normalize_metadata_dict(exif)
    except Exception:
        return exif


def read_xmp(path: str) -> Dict[str, Any]:
    xmp: Dict[str, Any] = {}

    def parse_xmp_xml(xmp_xml: str) -> Dict[str, Any]:
        """Parse XMP XML into a flat dict with local tag names.
        - Attributes on rdf:Description are included with their local names (e.g., Headline)
        - Child elements with rdf:li are collapsed into lists (or single string for title/description/rights)
        """
        out: Dict[str, Any] = {}
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xmp_xml)
            ns_rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
            for desc in root.findall('.//{' + ns_rdf + '}Description'):
                # Attributes (namespaced): strip namespace to local name
                for k, v in desc.attrib.items():
                    key = k.split('}', 1)[1] if '}' in k else k
                    out[key] = v
                # Child elements
                for child in desc:
                    tag = child.tag
                    tagname = tag.split('}', 1)[1] if '}' in tag else tag
                    li_nodes = child.findall('.//{' + ns_rdf + '}li')
                    if li_nodes:
                        li_texts = [ (li.text or '').strip() for li in li_nodes if (li.text or '').strip() ]
                        # Prefer single string for certain well-known fields
                        if tagname.lower() in ('title', 'description', 'rights', 'headline') and len(li_texts) == 1:
                            out[tagname if tagname != 'headline' else 'Headline'] = li_texts[0]
                        else:
                            out[tagname] = li_texts
                    else:
                        text = child.text
                        if text is not None and text.strip():
                            out[tagname] = text.strip()
        except Exception as e:
            # Fallback to raw packet if parsing fails
            return {"xmp_packet": xmp_xml, "error": f"xmp(parse): {e}"}
        return out

    # Try libxmp first
    if HAVE_LIBXMP:
        xf = None
        try:
            xf = XMPFiles(file_path=path)
            xmp_str = xf.get_xmp_str()
            if xmp_str:
                # Parse XMP string to extract fields (dc:subject, photoshop:Headline, etc.)
                parsed = parse_xmp_xml(xmp_str)
                xmp.update(parsed)
        except Exception as e:
            xmp = {"error": f"xmp(libxmp): {e}"}
        finally:
            if xf is not None:
                try:
                    xf.close_file()
                except Exception:
                    pass

    # Fallback: scan file for XMP packet
    if not xmp:
        try:
            data = Path(path).read_bytes()
            start = data.find(b"<x:xmpmeta")
            end = data.find(b"</x:xmpmeta>")
            if start != -1 and end != -1 and end > start:
                packet = data[start:end+12]
                packet_str = packet.decode('utf-8', errors='replace')
                # Parse packet to structured fields
                xmp = parse_xmp_xml(packet_str)
        except Exception as e:
            if not xmp:
                xmp = {"error": f"xmp(fallback): {e}"}

    try:
        return _normalize_metadata_dict(xmp)
    except Exception:
        return xmp


def read_all_metadata(path: str) -> Dict[str, Any]:
    return {
        "general": read_general(path),
        "exif": read_exif(path),
        "xmp": read_xmp(path),
    }


# -------------------- GUI --------------------

class ViewerApp(tk.Tk):
    def __init__(self, initial_path: Optional[str] = None):
        super().__init__()
        self.title("Image Metadata Viewer")
        self.geometry("900x700")

        # Controls
        btn_row = tk.Frame(self)
        btn_row.pack(fill=tk.X, padx=8, pady=6)

        tk.Button(btn_row, text="Open Image", command=self.on_open).pack(side=tk.LEFT)
        tk.Button(btn_row, text="Copy All", command=self.on_copy).pack(side=tk.LEFT, padx=(6,0))
        tk.Button(btn_row, text="Save JSON", command=self.on_save_json).pack(side=tk.LEFT, padx=(6,0))

        # Text area
        self.text = tk.Text(self, wrap=tk.NONE)
        self.text.configure(font=("Menlo", 11))
        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        yscroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Status
        self.status = tk.Label(self, anchor="w", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X)

        self.current_path: Optional[str] = None
        if initial_path:
            self.load_path(initial_path)

    def set_text(self, s: str):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", s)

    def on_open(self):
        path = filedialog.askopenfilename(title="Open Image",
                                          filetypes=[
                                              ("Images", "*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.gif;*.bmp"),
                                              ("All files", "*.*"),
                                          ])
        if path:
            self.load_path(path)

    def load_path(self, path: str):
        try:
            meta = read_all_metadata(path)
            pretty = json.dumps(meta, indent=2, ensure_ascii=False)
            self.set_text(pretty)
            self.current_path = path
            self.status.config(text=f"Loaded: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load metadata: {e}")

    def on_copy(self):
        try:
            s = self.text.get("1.0", tk.END)
            self.clipboard_clear()
            self.clipboard_append(s)
            self.status.config(text="Copied metadata to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {e}")

    def on_save_json(self):
        if not self.current_path:
            messagebox.showinfo("Save JSON", "Open an image first.")
            return
        try:
            dst = Path(self.current_path).with_suffix("")
            dst = dst.with_name(dst.name + "_metadata.json")
            s = self.text.get("1.0", tk.END)
            dst.write_text(s, encoding="utf-8")
            self.status.config(text=f"Saved: {dst}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path and not os.path.exists(path):
        print(f"File does not exist: {path}")
        sys.exit(2)
    app = ViewerApp(path)
    app.mainloop()


if __name__ == "__main__":
    main()
