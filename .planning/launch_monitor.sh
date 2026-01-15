#!/bin/bash
cd /home/mark/Repositories/livemathtex
echo '════════════════════════════════════════════════════════════════════'
echo '  🔄 LiveMathTeX Workflow Monitor'
echo '════════════════════════════════════════════════════════════════════'
echo ''
echo '  Watching: /home/mark/Repositories/livemathtex/.planning/'
echo '  - .debug-calculations-status.json (Cursor)'
echo '  - .build-all-status.json (Claude CLI)'
echo ''
echo '  Press Ctrl+C to stop monitoring'
echo '════════════════════════════════════════════════════════════════════'
echo ''
python scripts/monitor_debug_build.py --project-repo /home/mark/Repositories/livemathtex --interval 10
echo ''
echo 'Monitor stopped. Press Enter to close.'
read
