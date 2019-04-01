from typing import NamedTuple, List, Any
from gi.repository import Gtk
from gi.repository import Gdk


class HotKeys:
    class Entry(NamedTuple):
        key: int
        mode: Gdk.ModifierType
        args: List[Any]
        callback: Any

    def __init__(self):
        self.entries: List[HotKeys.Entry] = list()

    def add(self, key: int, mode: Gdk.ModifierType, args=None):
        if args is None:
            args = []

        def wrapper(func):
            self.entries.append(self.Entry(key, mode, args, func))
            return func
        return wrapper

    # noinspection PyDefaultArgument
    def apply_to_window(self, window: Gtk.Window):
        accel_group = Gtk.AccelGroup()
        for hot_key in self.entries:
            # noinspection PyDefaultArgument
            def callback(_group, _acceleratable, _keyval, _modifier, args=hot_key.args):
                hot_key.callback(window, *args)

            accel_group.connect(hot_key.key, hot_key.mode, 0, callback)
        window.add_accel_group(accel_group)
