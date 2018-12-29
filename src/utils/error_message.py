from gi.repository import Gtk


def show_error_message(parent, title, secondary):
    error_dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, title)
    error_dialog.format_secondary_text(secondary)
    error_dialog.run()
    error_dialog.destroy()
