# Watcher

## Setup

```
./tools/install.sh <installation path>
```

## Run

```
<alias or binary path> <path to watch> --callback=<python_module.py>:<functionName>
```

## Example

```
watcher ./some/path --callback=python_module.py:function_name
watcher ./some/path
```