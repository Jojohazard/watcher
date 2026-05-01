# Install dependencies

apk add python3 py3-pip build-base python3-dev

# Create and activate venv

python3 -m venv .venv
source .venv/bin/activate

# Install dependencies

pip install -r requirements.txt

pyinstaller --onefile src/main.py

# Install the binary

target="${1:-/usr/local/bin/watcher}"

if [[ -n "$1" && ! "$target" =~ watcher$ ]]; then
    target="${target}watcher"
fi

cp -v dist/main "$target"

alias_name="watcher"

if ! grep -q "alias $alias_name=" ~/.bashrc; then
    echo "alias $alias_name='$target'" >> ~/.bashrc
    echo "Alias added: $alias_name -> $target"
    echo "Run 'source ~/.bashrc' to activate the alias"
else
    echo "Alias '$alias_name' already exists in ~/.bashrc"
fi