from gi.repository import Gtk
from typing import Dict, Any, Optional, Callable, Set
import threading

Callback = Callable[[Set[Any], Dict[Any, str]], None]


class BufferWatcher:
    PARAMETERS = "parameters"

    def __init__(self, timeout: float, callback: Callback):
        self.timeout: float = timeout
        self.buffers: Dict[Any, Gtk.TextBuffer] = {}
        self.callback = callback
        self.start_rule = "start"
        self.parser = "earley"

        self._thread: Optional[threading.Timer] = None
        self._event: threading.Event = threading.Event()
        self._lock: threading.Lock = threading.Lock()
        self._running = False
        self._force_process = False
        self._changed = set()
        self._signals = dict()

    def add_buffer(self, name: Any, buffer: Gtk.TextBuffer):
        with self._lock:
            self.buffers[name] = buffer
            if self._running:
                self._signals[name] = buffer.connect("changed", lambda _: self._buffer_changed(name))
            self._event.set()

    def start(self):
        self._running = True
        self._thread = threading.Thread(name="BufferWatcherThread", target=self._thread_run)
        self._thread.start()
        self._changed = set(self.buffers.keys())
        for key in self.buffers:
            self._signals[key] = self.buffers[key].connect("changed", lambda _, key=key: self._buffer_changed(key))
        self._event.set()

    def set_parameters(self, start: Optional[str] = None, parser: Optional[str] = None):
        if start is not None:
            self.start_rule = start
        if parser is not None:
            self.parser = parser
        self._buffer_changed(BufferWatcher.PARAMETERS)

    def _buffer_changed(self, key):
        with self._lock:
            self._changed.add(key)
            self._event.set()

    def stop(self):
        with self._lock:
            self._running = False
        self._event.set()
        self._thread.join()
        self._event.clear()

        for key in self._signals:
            self.buffers[key].disconnect(self._signals[key])
        self._signals.clear()

    def _thread_run(self):
        self._lock.acquire()

        running = self._running
        while running:
            has_changes = len(self._changed) > 0
            self._lock.release()
            wait_result = self._event.wait(self.timeout) if has_changes else self._event.wait()
            self._lock.acquire()

            if not wait_result or self._force_process:
                text = dict()
                for key in self.buffers:
                    buffer = self.buffers[key]
                    text[key] = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
                self.callback(self._changed, text)
                self._changed.clear()
                self._force_process = False
            running = self._running
            self._event.clear()
        self._lock.release()

    def force_processing(self):
        self._force_process = True
        self._event.set()
