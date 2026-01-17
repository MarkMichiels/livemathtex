#!/bin/bash
# =============================================================================
# setup_symlinks.sh - LiveMathTeX Development Symlinks
# =============================================================================
#
# PURPOSE:
#   Creates symlinks to proviron for shared development tools.
#   This is only needed for local development in the axabio workspace.
#
# WHAT IT DOES:
#   - Symlinks tools/, scripts/, .crossnote/ from proviron
#   - Sets up .cursor/rules/ index (explains multi-root workspace)
#
# WHAT IT DOES NOT DO:
#   - Does NOT register commands to ~/.claude/ (mark-private does that)
#   - Does NOT symlink Cursor rules (multi-root workspace handles that)
#
# FOR CLAUDE CODE:
#   Run ~/Repositories/mark-private/setup_claude_commands.sh instead.
#   That creates folder symlinks: ~/.claude/commands/lmt/ -> this repo
#
# STANDALONE DEVELOPMENT:
#   If developing LiveMathTeX outside the axabio workspace, symlinks
#   are optional. The project works independently.
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIRON_DIR="$(dirname "$SCRIPT_DIR")/proviron"

echo "=== LiveMathTeX Symlink Setup ==="
echo ""

# Verify proviron exists
if [ ! -d "$PROVIRON_DIR" ]; then
    echo "Note: Proviron not found at $PROVIRON_DIR"
    echo "      This is OK for standalone development."
    echo "      Symlinks will not be created."
    exit 0
fi

# =============================================================================
# Symlink shared directories from proviron
# =============================================================================

create_symlink() {
    local source="$1"
    local target="$2"
    local name="$3"

    if [ ! -d "$source" ]; then
        echo "SKIP: $name (not found in proviron)"
        return
    fi

    if [ -L "$target" ]; then
        if [ "$(readlink "$target")" == "$source" ]; then
            echo "OK:   $name (already linked)"
            return
        fi
        rm "$target"
    elif [ -d "$target" ]; then
        echo "SKIP: $name (local directory exists)"
        return
    fi

    ln -s "$source" "$target"
    echo "LINK: $name -> proviron"
}

echo "Setting up shared directories..."
create_symlink "$PROVIRON_DIR/tools" "$SCRIPT_DIR/tools" "tools/"
create_symlink "$PROVIRON_DIR/scripts" "$SCRIPT_DIR/scripts" "scripts/"
create_symlink "$PROVIRON_DIR/.crossnote" "$SCRIPT_DIR/.crossnote" ".crossnote/"

# =============================================================================
# .cursor/rules/ - Explain multi-root workspace
# =============================================================================

echo ""
echo "Setting up .cursor/rules/..."
mkdir -p "$SCRIPT_DIR/.cursor/rules"

# Clean up any old proviron rule symlinks
for link in "$SCRIPT_DIR/.cursor/rules/"*; do
    [ -L "$link" ] || continue
    target=$(readlink "$link")
    if [[ "$target" == *"proviron"* ]]; then
        rm "$link"
        echo "CLEAN: Removed old proviron symlink: $(basename "$link")"
    fi
done

# Create/update index explaining the setup
cat > "$SCRIPT_DIR/.cursor/rules/index.md" << 'EOF'
# LiveMathTeX Cursor Rules

## Multi-Root Workspace

In the axabio multi-root workspace, Cursor automatically loads rules from
all workspace folders. Proviron rules (general, python, documentation, etc.)
are available without symlinks.

**Do NOT symlink proviron rules here** - this causes duplicate loading!

## Local Rules

Add LiveMathTeX-specific rules here as `.mdc` files if needed.

## Claude Code Commands

LiveMathTeX commands are available as `/lmt:*` in Claude Code.
Run `~/Repositories/mark-private/setup_claude_commands.sh` to set up.
EOF
echo "OK:   .cursor/rules/index.md"

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Symlinks: tools/, scripts/, .crossnote/ -> proviron"
echo ""
echo "For Claude Code commands, run:"
echo "  ~/Repositories/mark-private/setup_claude_commands.sh"
echo ""
