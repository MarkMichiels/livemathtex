#!/bin/bash
cd /home/mark/Repositories/livemathtex
PIPE="/home/mark/Repositories/livemathtex/.planning/.claude-command-pipe"
mkdir -p .planning
rm -f "$PIPE"
mkfifo "$PIPE"

echo '════════════════════════════════════════════════════════════════════'
echo '  🔨 Claude CLI - FULLY AUTOMATED'
echo '════════════════════════════════════════════════════════════════════'
echo ''
echo '  Directory: /home/mark/Repositories/livemathtex'
echo "  Command pipe: $PIPE"
echo ''
echo '  ✅ FULLY AUTOMATIC:'
echo '     - Monitor detects new issues → sends /gsd:build-all'
echo '     - Claude receives command automatically'
echo '     - No manual intervention needed!'
echo ''
echo '  Starting Claude CLI with command pipe...'
echo '════════════════════════════════════════════════════════════════════'
echo ''

while true; do
    if read -r cmd < "$PIPE" 2>/dev/null; then
        echo "[MONITOR] Received command: $cmd"
        echo "$cmd"
    fi
done | claude --dangerously-skip-permissions

rm -f "$PIPE"
echo ''
echo 'Claude CLI exited. Press Enter to close.'
read
