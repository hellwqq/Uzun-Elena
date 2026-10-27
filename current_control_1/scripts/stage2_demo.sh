#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
python3 tools/make_vfs.py > /dev/null

echo "=== 1. no parameters (commands come from stdin) ==="
printf 'conf-dump\nexit\n' | python3 src/main.py

echo
echo "=== 2. --script only ==="
python3 src/main.py --script examples/startup/conf.emu

echo
echo "=== 3. --vfs and --script together ==="
python3 src/main.py --vfs examples/vfs/files.zip \
    --script examples/startup/conf.emu

echo
echo "=== 4. missing startup script ==="
python3 src/main.py --script no-such-file.emu
echo "exit code: $?"

echo
echo "=== 5. unknown option ==="
python3 src/main.py --bogus
echo "exit code: $?"
