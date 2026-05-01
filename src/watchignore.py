from dataclasses import dataclass
from typing import List, Union
from pathlib import Path
import os

@dataclass
class Dir:
    path: Path
    ignore: List[str]
    children: List[Union[str, 'Dir']]
    
def read_watchignore(file_path: Path) -> List[str]:
    with file_path.open("r") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines
    
def build_dir_tree(root: Path):
    children: List[Union[str, 'Dir']] = []
    ignore: List[str] = []
    
    for child in root.iterdir():
        child_path = child.resolve()
        
        if os.path.isdir(child_path):
            children.append(build_dir_tree(child_path))
            continue
        
        children.append(child_path)
        
        if (str(child_path).endswith('.watchignore')):
            ignore.extend(read_watchignore(child_path))
        pass
    
    return Dir(
        path=root.resolve(),
        ignore=ignore,
        children=children
    )
    
def build_flat_ignore_list(dir_obj: Dir) -> List[str]:
    top_path = dir_obj.path.resolve()
    flat_list: List[str] = []

    def _recurse(d: Dir):
        for pattern in d.ignore:
            relative_dir = d.path.resolve().relative_to(top_path)
            if relative_dir == Path('.'):
                flat_list.append(pattern)
            else:
                flat_list.append(str(relative_dir / pattern))
        for child in d.children:
            if isinstance(child, Dir):
                _recurse(child)

    _recurse(dir_obj)
    return flat_list

def debug_dir_tree(dir_obj: Dir, indent: int = 0):
    prefix = '  ' * indent
    print(f"{prefix}- Dir: {dir_obj.path}")
    if dir_obj.ignore:
        print(f"{prefix}  Ignore: {dir_obj.ignore}")

    for child in dir_obj.children:
        if isinstance(child, Dir):
            debug_dir_tree(child, indent + 1)
        else:
            print(f"{prefix}  - File: {child}")
            pass
        pass
    pass