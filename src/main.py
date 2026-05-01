import typer
from helpers import load_callback
from pathlib import Path
from handler_wrapper import HandlerWrapper
from watchdog.events import FileSystemEvent
from datetime import datetime
from watchignore import build_dir_tree, build_flat_ignore_list
from watcher import Watcher

def default_callback(event: FileSystemEvent):
    print(event.event_type, event.src_path, datetime.now())

app = typer.Typer()

@app.command()
def watch(
    path: str,
    callback: str | None = None
):
    path = Path(path)
    
    excluded_patterns = build_flat_ignore_list(build_dir_tree(path))
    
    if callback:
        callback = load_callback(callback)
    else:
        callback = default_callback
        
    handler_wrapper = HandlerWrapper(
        callback=callback,
        exclude_patterns=excluded_patterns
    )
    
    watcher = Watcher(
        path=path,
        handler_wrapper=handler_wrapper
    )
    
    watcher.start()
    
    pass

if __name__ == "__main__":
    app()