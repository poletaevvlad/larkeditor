import gi

gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version("GtkSource", "3.0")  # noqa: E402

import signal
import sys
from larkeditor.application import Application

signal.signal(signal.SIGINT, signal.SIG_DFL)
app = Application()
app.run(sys.argv)
