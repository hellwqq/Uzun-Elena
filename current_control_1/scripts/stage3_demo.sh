#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py > /dev/null

for name in empty minimal files deep; do
    echo "=== VFS variant: $name.zip ==="
    python3 src/main.py --vfs "examples/vfs/$name.zip" \
        --script examples/startup/vfs.emu
    echo
done

echo "=== no VFS given: empty VFS in memory ==="
python3 src/main.py --script examples/startup/vfs.emu

echo
echo "=== missing VFS file ==="
python3 src/main.py --vfs examples/vfs/nothing.zip
echo "exit code: $?"

echo
echo "=== file that is not a ZIP archive ==="
python3 src/main.py --vfs README.md
echo "exit code: $?"
