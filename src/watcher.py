from pathlib import Path
from handler_wrapper import HandlerWrapper
from watchdog.observers import Observer
import time

class Watcher:
    def __init__(
        self,
        path: Path,
        handler_wrapper: HandlerWrapper,
        recursive=True
    ):
        self.path = path
        self.handler_wrapper = handler_wrapper
        self.recursive = recursive
        pass
    
    def start(self):
        observer = Observer()
        
        observer.schedule(
            self.handler_wrapper.handler,
            str(self.path),
            recursive=self.recursive
        )
        
        observer.start()
        
        try:
            while True:
                time.sleep(1000)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join();
        pass
    pass