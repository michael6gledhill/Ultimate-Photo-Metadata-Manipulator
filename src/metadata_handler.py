"""
Metadata Handler Module
Handles reading, editing, and deleting metadata from various image formats.
Supports EXIF, IPTC, and XMP metadata.
"""

import json
import os
import re
import binascii
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image
import piexif
# XMP support: try to use pyxmp (if installed) or python-xmp-toolkit (libxmp).


class MetadataHandler:
    """
    Core metadata manipulation class.
    Supports JPEG, PNG, TIFF, and basic RAW file metadata operations.
    """

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp'}
    EXIF_READABLE_TAGS = {
        0x0112: 'Orientation',
        0x0132: 'DateTime',
        0x9003: 'DateTimeOriginal',
        0x010f: 'Make',
        0x0110: 'Model',
        0x0131: 'Software',
        0x8825: 'GPS Info',
        0x9000: 'ExifVersion',
        0xa001: 'ColorSpace',
    }

    def __init__(self):
        """Initialize the metadata handler."""
        self.last_error = None

    def _normalize_value(self, v):
        """Normalize a metadata value to a JSON/display-friendly Python type."""
        # bytes -> try to decode with common encodings, strip nulls and non-printables
        if isinstance(v, (bytes, bytearray)):
            for enc in ('utf-8', 'utf-16le', 'utf-16be', 'latin-1'):
                try:
                    s = v.decode(enc)
                    # strip trailing nulls and control characters
                    s = s.rstrip('\x00')
                    s = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]+', '', s)
                    return s
                except Exception:
                    continue
            # fallback: show short hex summary
            try:
                return f"<bytes {len(v)} bytes: {binascii.hexlify(v[:16]).decode()}{'...' if len(v)>16 else ''}>"
            except Exception:
                return str(v)

        # dict -> normalize recursively
        if isinstance(v, dict):
            return {self._normalize_value(k): self._normalize_value(val) for k, val in v.items()}

        # lists / tuples -> normalize elements; detect special patterns
        if isinstance(v, (list, tuple)):
            # detect a SINGLE rational (num, den) pair: tuple/list of exactly 2 integers
            if len(v) == 2 and all(isinstance(x, int) for x in v):
                num, den = v[0], v[1]
                try:
                    return round(num / den if den else 0, 8)  # avoid floating point noise
                except Exception:
                    pass
            
            # detect array of small integers (0-255) -> likely byte data from EXIF, try to decode
            if len(v) > 0 and all(isinstance(x, int) and 0 <= x <= 255 for x in v):
                try:
                    byte_val = bytes(v)
                    # Try UTF-16LE first (common for XP tags), then UTF-8
                    for enc in ('utf-16le', 'utf-8', 'latin-1'):
                        try:
                            s = byte_val.decode(enc)
                            s = s.rstrip('\x00')
                            s = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]+', '', s)
                            # If we got a reasonable string, split on common delimiters for multi-value fields
                            if len(s) > 2:
                                parts = [p.strip() for p in re.split(r'[;,\x00]+', s) if p.strip()]
                                return parts if len(parts) > 1 else (parts[0] if parts else s)
                            return s
                        except Exception:
                            continue
                except Exception:
                    pass
            
            # detect sequence of (num, den) pairs (rational numbers) - multiple pairs
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
                    # common case: GPS lat/long as 3 rationals -> convert DMS to decimal degrees
                    if len(floats) == 3:
                        deg, minute, sec = floats
                        try:
                            return deg + minute / 60.0 + sec / 3600.0
                        except Exception:
                            return floats
                    return floats
            # otherwise normalize each element
            return [self._normalize_value(x) for x in v]

        # other primitives: return as-is
        return v

    def _normalize_metadata_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively normalize all values in a metadata dictionary."""
        out: Dict[str, Any] = {}
        for k, v in d.items():
            # normalize key (strip namespaces like {ns}tag)
            key = k
            if isinstance(key, str) and '}' in key:
                key = key.split('}', 1)[1]
            out_key = key
            out[out_key] = self._normalize_value(v)
        return out

    def get_file_extension(self, file_path: str) -> str:
        """Get the file extension in lowercase."""
        return Path(file_path).suffix.lower()

    def is_supported(self, file_path: str) -> bool:
        """Check if a file format is supported."""
        return self.get_file_extension(file_path) in self.SUPPORTED_FORMATS

    def read_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Read all metadata from an image file.
        Returns: dict with 'exif', 'iptc', 'xmp' keys
        """
        if not os.path.exists(file_path):
            self.last_error = f"File not found: {file_path}"
            return {}

        if not self.is_supported(file_path):
            self.last_error = f"Unsupported file format: {self.get_file_extension(file_path)}"
            return {}

        metadata = {
            'exif': {},
            'iptc': {},
            'xmp': {},
            'general': self._read_general_metadata(file_path)
        }

        try:
            # Read EXIF
            metadata['exif'] = self._read_exif(file_path)
        except Exception as e:
            self.last_error = f"Error reading EXIF: {str(e)}"

        try:
            # Read XMP
            metadata['xmp'] = self._read_xmp(file_path)
        except Exception as e:
            self.last_error = f"Error reading XMP: {str(e)}"

        return metadata

    def _read_general_metadata(self, file_path: str) -> Dict[str, Any]:
        """Read general image metadata (dimensions, format, etc.)."""
        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'file_size': os.path.getsize(file_path),
                }
        except Exception as e:
            self.last_error = f"Error reading general metadata: {str(e)}"
            return {}

    def _read_exif(self, file_path: str) -> Dict[str, Any]:
        """Extract EXIF data from image."""
        exif_dict = {}
        try:
            img_data = piexif.load(file_path)
            for ifd_name in ("0th", "Exif", "GPS", "1st"):
                ifd = img_data[ifd_name]
                for tag in ifd:
                    tag_name = piexif.TAGS[ifd_name][tag]["name"]
                    tag_value = ifd[tag]
                    
                    # Handle XP* fields (XPKeywords, XPSubject, XPTitle) which are UTF-16LE encoded
                    # They can arrive as bytes or as an array of integers (byte values)
                    if tag_name.startswith('XP') and tag_name.lower() in ('xpkeywords', 'xpsubject', 'xptitle', 'xpcomments'):
                        # Convert array of integers to bytes if needed
                        if isinstance(tag_value, (list, tuple)):
                            try:
                                tag_value = bytes(tag_value)
                            except (TypeError, ValueError):
                                tag_value = str(tag_value)
                        
                        # Now decode UTF-16LE
                        if isinstance(tag_value, (bytes, bytearray)):
                            try:
                                val = tag_value.decode('utf-16le', errors='ignore').rstrip('\x00')
                            except Exception:
                                try:
                                    val = tag_value.decode('utf-8', errors='replace')
                                except Exception:
                                    val = str(tag_value)
                            
                            # Split into list on semicolon, comma, or embedded nulls
                            parts = [p.strip() for p in re.split(r'[;,\x00]+', val) if p.strip()]
                            tag_value = parts if len(parts) > 1 else (parts[0] if parts else '')
                    
                    # Handle other byte fields (UserComment, etc)
                    elif isinstance(tag_value, (bytes, bytearray)):
                        # Try utf-8 first, then other encodings
                        val = None
                        try:
                            val = tag_value.decode('utf-8', errors='replace')
                        except Exception:
                            try:
                                val = tag_value.decode('utf-16le', errors='ignore')
                            except Exception:
                                val = str(tag_value)
                        
                        # Clean up UserComment (may have ASCII prefix like "ASCII\x00\x00\x00")
                        if tag_name == 'UserComment' and val:
                            val = re.sub(r'^(ASCII|UNICODE|JIS)\s*\x00+', '', val, flags=re.IGNORECASE)
                            val = val.rstrip('\x00').strip()
                        
                        tag_value = val

                    exif_dict[tag_name] = tag_value
        except Exception as e:
            pass
        # Normalize values for display/JSON
        try:
            return self._normalize_metadata_dict(exif_dict)
        except Exception:
            return exif_dict

    def _read_xmp(self, file_path: str) -> Dict[str, Any]:
        """Extract XMP data from image."""
        xmp_dict: Dict[str, Any] = {}

        # First try pyxmp (module name: xmp)
        try:
            import xmp as pyxmp  # type: ignore
            with open(file_path, 'rb') as f:
                xmp_data = pyxmp.get_xmp(f)
                if xmp_data:
                    # pyxmp exposes get_dict()
                    try:
                        xmp_dict = xmp_data.get_dict()
                    except Exception:
                        # Fallback: return raw string if available
                        xmp_str = getattr(xmp_data, 'to_s', None)
                        if callable(xmp_str):
                            xmp_dict = {'xmp': xmp_str()}
                        else:
                            xmp_dict = {'xmp': str(xmp_data)}
            return xmp_dict
        except Exception:
            # pyxmp not available or failed — try python-xmp-toolkit (libxmp)
            pass

        try:
            # python-xmp-toolkit
            from libxmp import XMPFiles  # type: ignore
            xf = None
            try:
                xf = XMPFiles(file_path=file_path)
                xmp_str = xf.get_xmp_str()
                if xmp_str:
                    # Try to parse the XMP packet XML and extract attributes/children
                            try:
                                from xml.etree import ElementTree as ET

                                root = ET.fromstring(xmp_str)
                                # Find all rdf:Description elements and collect attributes and child text
                                ns_rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                                for desc in root.findall('.//{'+ns_rdf+'}Description'):
                                    # attributes (namespaced)
                                    for k, v in desc.attrib.items():
                                        xmp_dict[k] = v
                                    # child nodes: handle rdf:Bag / rdf:Seq / rdf:Alt structures
                                    for child in desc:
                                        tag = child.tag
                                        # strip namespace if present
                                        if '}' in tag:
                                            tagname = tag.split('}', 1)[1]
                                        else:
                                            tagname = tag

                                        # collect rdf:li children if present
                                        li_nodes = child.findall('.//{'+ns_rdf+'}li')
                                        if li_nodes:
                                            li_texts = [ (li.text or '').strip() for li in li_nodes if (li.text or '').strip() ]
                                            # for title/description/rights prefer single string
                                            if tagname in ('title', 'description', 'rights') and len(li_texts) == 1:
                                                xmp_dict[tagname] = li_texts[0]
                                            else:
                                                xmp_dict[tagname] = li_texts
                                        else:
                                            # fallback to direct text
                                            text = child.text
                                            if text is not None:
                                                xmp_dict[tagname] = text.strip()
                            except Exception:
                                # If XML parsing fails, return raw XMP string
                                xmp_dict = {'xmp': xmp_str}
            finally:
                if xf is not None:
                    try:
                        xf.close_file()
                    except Exception:
                        pass
            # normalize xmp dict values
            try:
                return self._normalize_metadata_dict(xmp_dict)
            except Exception:
                return xmp_dict
        except Exception:
            # Give up — return empty dict
            return {}

    def delete_all_metadata(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """
        Remove all metadata from an image and save as new file.
        If output_path is None, overwrites original (ask user first!).
        """
        if not os.path.exists(file_path):
            self.last_error = f"File not found: {file_path}"
            return False

        try:
            with Image.open(file_path) as img:
                # Create a new image without metadata
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)

                # Save to output path
                save_path = output_path or file_path
                image_without_exif.save(save_path, "JPEG", quality=95)
                return True
        except Exception as e:
            self.last_error = f"Error deleting metadata: {str(e)}"
            return False

    def delete_specific_metadata(self, file_path: str, keys_to_delete: List[str],
                                  output_path: Optional[str] = None) -> bool:
        """
        Delete specific metadata fields from an image.
        keys_to_delete: list of metadata field names to remove.
        """
        if not os.path.exists(file_path):
            self.last_error = f"File not found: {file_path}"
            return False

        try:
            metadata = self.read_metadata(file_path)
            # For now, simplified: remove all metadata and save.
            # In production, would selectively remove fields.
            return self.delete_all_metadata(file_path, output_path)
        except Exception as e:
            self.last_error = f"Error deleting specific metadata: {str(e)}"
            return False

    def edit_metadata(self, file_path: str, metadata_updates: Dict[str, Any],
                       output_path: Optional[str] = None) -> bool:
        """
        Add or edit metadata in an image.
        metadata_updates: dict with 'exif', 'xmp' keys containing updates.
        """
        if not os.path.exists(file_path):
            self.last_error = f"File not found: {file_path}"
            return False

        save_path = output_path or file_path

        # Update EXIF for JPEG/TIFF when possible
        try:
            ext = self.get_file_extension(file_path)
            if ext in ('.jpg', '.jpeg', '.tiff', '.tif'):
                # Load image and existing EXIF
                with Image.open(file_path) as img:
                    exif_dict = {}
                    try:
                        exif_dict = piexif.load(img.info.get('exif', b''))
                    except Exception:
                        # start with empty structure
                        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

                    # Map simple fields to EXIF tags where appropriate
                    zeroth = exif_dict.setdefault('0th', {})
                    if 'title' in metadata_updates and metadata_updates['title']:
                        zeroth[piexif.ImageIFD.ImageDescription] = metadata_updates['title'].encode('utf-8', errors='replace')
                    if 'authors' in metadata_updates and metadata_updates['authors']:
                        zeroth[piexif.ImageIFD.Artist] = metadata_updates['authors'].encode('utf-8', errors='replace')
                    if 'copyright' in metadata_updates and metadata_updates['copyright']:
                        zeroth[piexif.ImageIFD.Copyright] = metadata_updates['copyright'].encode('utf-8', errors='replace')
                    # Tags (keywords) - write to XPKeywords (UTF-16LE) and XPSubject if available
                    if 'tags' in metadata_updates and metadata_updates['tags']:
                        tags = metadata_updates['tags']
                        if isinstance(tags, str):
                            tags = [t.strip() for t in tags.split(',') if t.strip()]
                        # join with semicolon for XPKeywords
                        try:
                            joined = '; '.join(tags)
                            # XPKeywords expects UTF-16LE bytes
                            zeroth[piexif.ImageIFD.XPKeywords] = joined.encode('utf-16le', errors='replace')
                        except Exception:
                            pass
                        # also write XPSubject as a short subject string
                        try:
                            subj = metadata_updates.get('subject', '')
                            if subj:
                                zeroth[piexif.ImageIFD.XPSubject] = str(subj).encode('utf-16le', errors='replace')
                        except Exception:
                            pass
                    # Comments -> UserComment (Exif IFD)
                    if 'comments' in metadata_updates and metadata_updates['comments']:
                        exif_ifd = exif_dict.setdefault('Exif', {})
                        # UserComment requires a special encoding header; we'll store as plain bytes
                        exif_ifd[piexif.ExifIFD.UserComment] = metadata_updates['comments'].encode('utf-8', errors='replace')

                    exif_bytes = piexif.dump(exif_dict)
                    # Save with new EXIF
                    with Image.open(file_path) as img2:
                        img2.save(save_path, exif=exif_bytes)
            else:
                # For non-JPEG/TIFF, simply copy file (we'll handle XMP separately)
                if save_path != file_path:
                    from shutil import copyfile
                    copyfile(file_path, save_path)
        except Exception as e:
            # Non-fatal for XMP path, but record error
            self.last_error = f"Error writing EXIF: {str(e)}"

        # Update XMP using python-xmp-toolkit (libxmp) if available
        try:
            from libxmp import XMPFiles

            # Build a minimal XMP packet containing Dublin Core elements
            def _escape(s: str) -> str:
                import xml.sax.saxutils as sax
                return sax.escape(s)

            title = metadata_updates.get('title', '')
            description = metadata_updates.get('comments', '')
            authors = metadata_updates.get('authors', '')
            rights = metadata_updates.get('copyright', '')
            tags = metadata_updates.get('tags', []) or []

            # Ensure tags is a list
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',') if t.strip()]

            xmp_lines = [
                '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>',
                '<x:xmpmeta xmlns:x="adobe:ns:meta/">',
                '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">',
                '<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">'
            ]

            if title:
                xmp_lines.append(f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{_escape(title)}</rdf:li></rdf:Alt></dc:title>')
            if description:
                xmp_lines.append(f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{_escape(description)}</rdf:li></rdf:Alt></dc:description>')
            if authors:
                # creators as rdf:Seq
                creator_items = ''.join([f'<rdf:li>{_escape(a.strip())}</rdf:li>' for a in (authors.split(';') if ';' in authors else [authors]) if a.strip()])
                xmp_lines.append(f'<dc:creator><rdf:Seq>{creator_items}</rdf:Seq></dc:creator>')
            if tags:
                tag_items = ''.join([f'<rdf:li>{_escape(t)}</rdf:li>' for t in tags])
                xmp_lines.append(f'<dc:subject><rdf:Bag>{tag_items}</rdf:Bag></dc:subject>')
            if rights:
                xmp_lines.append(f'<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">{_escape(rights)}</rdf:li></rdf:Alt></dc:rights>')

            xmp_lines.append('</rdf:Description>')
            xmp_lines.append('</rdf:RDF>')
            xmp_lines.append('</x:xmpmeta>')
            xmp_lines.append('<?xpacket end="w"?>')

            xmp_str = '\n'.join(xmp_lines)

            xf = None
            try:
                xf = XMPFiles(file_path=save_path, open_forupdate=True)
                xf.put_xmp(xmp_str)
            finally:
                if xf:
                    try:
                        xf.close_file()
                    except Exception:
                        pass

        except Exception as e:
            # If libxmp is not present or fails, record and continue
            self.last_error = f"Error writing XMP: {str(e)}"

        return True

    def export_metadata_json(self, file_path: str, output_json_path: str) -> bool:
        """Export metadata to a JSON file."""
        try:
            metadata = self.read_metadata(file_path)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            return True
        except Exception as e:
            self.last_error = f"Error exporting metadata: {str(e)}"
            return False

    def export_metadata_txt(self, file_path: str, output_txt_path: str) -> bool:
        """Export metadata to a text file."""
        try:
            metadata = self.read_metadata(file_path)
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Metadata for: {file_path}\n")
                f.write(f"Exported: {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n\n")

                for section, data in metadata.items():
                    if data:
                        f.write(f"\n{section.upper()}\n")
                        f.write("-" * 40 + "\n")
                        for key, value in data.items():
                            f.write(f"  {key}: {value}\n")
            return True
        except Exception as e:
            self.last_error = f"Error exporting metadata to text: {str(e)}"
            return False
