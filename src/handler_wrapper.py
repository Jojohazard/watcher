import threading
from typing import Callable
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from pathlib import Path
import pathspec
import time


class HandlerWrapper:
    def __init__(
        self,
        callback: Callable[[FileSystemEvent], None] | None = None,
        watch_file_created: bool = True,
        watch_file_modified: bool = True,
        watch_file_deleted: bool = True,
        debounced: bool = False,
        debounce_delay: float = 0.3,
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
        watch_path: Path | None = None
    ):
        self.callback = callback
        self.debounced = debounced
        self.debounce_delay = debounce_delay
        self._debounce_timer: threading.Timer | None = None
        self._last_event: FileSystemEvent | None = None
        self._lock = threading.Lock()
        self._pending_files: dict[str, float] = {}  # file path -> last event timestamp

        self.watch_path = Path(watch_path) if watch_path else Path(".")
        self.include_spec = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns or [])
        self.exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude_patterns or [])

        self.handler = FileSystemEventHandler()

        def callback_wrapper(event: FileSystemEvent):
            if event.is_directory:
                return

            try:
                rel_path = str(Path(event.src_path).relative_to(self.watch_path))
            except ValueError:
                return

            if self.include_spec and not self.include_spec.match_file(rel_path):
                return
            if self.exclude_spec and self.exclude_spec.match_file(rel_path):
                return

            now = time.time()
            with self._lock:
                last_ts = self._pending_files.get(rel_path, 0)
                if now - last_ts < self.debounce_delay:
                    # Too soon, ignore duplicate
                    return

                self._pending_files[rel_path] = now
                self._last_event = event

                if self.debounced:
                    if self._debounce_timer:
                        self._debounce_timer.cancel()
                    self._debounce_timer = threading.Timer(
                        self.debounce_delay, self._fire_callback
                    )
                    self._debounce_timer.start()
                else:
                    self.callback(event)

        if watch_file_created:
            self.handler.on_created = callback_wrapper
        if watch_file_modified:
            self.handler.on_modified = callback_wrapper
        if watch_file_deleted:
            self.handler.on_deleted = callback_wrapper

    def _fire_callback(self):
        with self._lock:
            if self.callback and self._last_event:
                self.callback(self._last_event)
            self._last_event = None
            self._debounce_timer = None
            self._pending_files.clear()  # reset for next events