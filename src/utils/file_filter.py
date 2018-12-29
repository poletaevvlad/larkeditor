from typing import Optional, List
from gi.repository import Gtk


def create_file_filter(name: str, mime_types: Optional[List[str]] = None, patterns: Optional[List[str]] = None):
    file_filter: Gtk.FileFilter = Gtk.FileFilter()
    file_filter.set_name(name)
    if mime_types is not None:
        for mime_type in mime_types:
            file_filter.add_mime_type(mime_type)
    if patterns is not None:
        for pattern in patterns:
            file_filter.add_pattern(pattern)
    return file_filter
