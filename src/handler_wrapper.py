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
        debounced: bool = True,
        debounce_delay: float = 0.3,
        cooldown: float = 10.0,                  # NEW: cooldown period per file
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
        watch_path: Path | None = None
    ):
        self.callback = callback
        self.debounced = debounced
        self.debounce_delay = debounce_delay
        self.cooldown = cooldown
        self._lock = threading.Lock()

        # Maps: file -> timer
        self._file_timers: dict[str, threading.Timer] = {}
        # Cooldown tracker: file -> last fired timestamp
        self._file_last_fired: dict[str, float] = {}

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
                # Check cooldown
                last_fired = self._file_last_fired.get(rel_path, 0)
                if now - last_fired < self.cooldown:
                    return  # still in cooldown, ignore

                def fire():
                    with self._lock:
                        if self.callback:
                            self.callback(event)
                        # mark last fired time
                        self._file_last_fired[rel_path] = time.time()
                        self._file_timers.pop(rel_path, None)

                if self.debounced:
                    # Cancel existing debounce timer
                    if rel_path in self._file_timers:
                        self._file_timers[rel_path].cancel()
                    timer = threading.Timer(self.debounce_delay, fire)
                    self._file_timers[rel_path] = timer
                    timer.start()
                else:
                    fire()

        if watch_file_created:
            self.handler.on_created = callback_wrapper
        if watch_file_modified:
            self.handler.on_modified = callback_wrapper
        if watch_file_deleted:
            self.handler.on_deleted = callback_wrapper