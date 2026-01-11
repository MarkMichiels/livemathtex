#!/bin/bash
# setup_symlinks.sh - Setup symlinks to proviron for shared development standards
#
# This script creates symlinks to proviron's:
# - Shared tools and scripts (optional)
#
# Note: Cursor rules are NOT symlinked - they're available via multi-root workspace.
# Local rules can be added directly to .cursor/rules/ (tracked in git).
#
# LiveMathTeX is a standalone project, but during development in the
# axabio workspace, we benefit from shared coding standards.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIRON_DIR="$(dirname "$SCRIPT_DIR")/proviron"

echo "=== LiveMathTeX Symlink Setup ==="
echo "Script directory: $SCRIPT_DIR"
echo "Proviron directory: $PROVIRON_DIR"
echo ""

# Verify proviron exists
if [ ! -d "$PROVIRON_DIR" ]; then
    echo "⚠️  Proviron not found at $PROVIRON_DIR"
    echo "   This is OK if you're developing LiveMathTeX standalone."
    echo "   Symlinks will not be created."
    exit 0
fi

# =============================================================================
# .cursor/rules/ - Local rules only (NO symlinks from proviron!)
# =============================================================================
# IMPORTANT: In a multi-root workspace, Cursor loads rules from ALL folders.
# Since proviron is part of the workspace, its rules are already available.
# Symlinking them here would cause duplicate rule loading.
# =============================================================================
echo "📁 Setting up .cursor/rules/..."

mkdir -p "$SCRIPT_DIR/.cursor/rules"

# Clean up any existing symlinks to proviron rules (from previous setup)
echo "   Cleaning up old proviron rule symlinks..."
for SYMLINK in "$SCRIPT_DIR/.cursor/rules/"*; do
    [ -L "$SYMLINK" ] || continue
    TARGET=$(readlink "$SYMLINK")
    if [[ "$TARGET" == "$PROVIRON_DIR/.cursor/rules/"* ]]; then
        rm "$SYMLINK"
        echo "   ✅ Removed $(basename "$SYMLINK") (proviron symlink - no longer needed)"
    fi
done

# Create rules index if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.cursor/rules/index.md" ]; then
    cat > "$SCRIPT_DIR/.cursor/rules/index.md" << 'EOF'
# LiveMathTeX Cursor Rules

This directory contains Cursor rules specific to the LiveMathTeX project.

## Multi-Root Workspace

In a multi-root workspace (development.code-workspace), Cursor automatically
loads rules from all workspace folders. Since proviron is in the workspace,
its rules (general, python, documentation, etc.) are already available.

**Do NOT symlink proviron rules here** - this causes duplicate loading!

## Local Rules

Add LiveMathTeX-specific rules here as `.mdc` files:
- `livemathtex.mdc` - LiveMathTeX-specific coding standards (if needed)

## Standalone Development

If developing LiveMathTeX outside the multi-root workspace, you may want to
copy (not symlink) relevant rules from proviron manually.
EOF
    echo "   ✅ Created/updated index.md"
else
    echo "   ℹ️  index.md exists (not overwriting)"
fi

# =============================================================================
# .cursor/commands/ - LiveMathTeX specific commands (not symlinked)
# =============================================================================
echo ""
echo "📁 Setting up .cursor/commands/..."
mkdir -p "$SCRIPT_DIR/.cursor/commands"

if [ ! -f "$SCRIPT_DIR/.cursor/commands/README.md" ]; then
    cat > "$SCRIPT_DIR/.cursor/commands/README.md" << 'EOF'
# LiveMathTeX Cursor Commands

This directory contains Cursor commands specific to LiveMathTeX development.

## Available Commands

(Add commands here as needed)

## Usage

Type `/command-name` in Cursor chat to execute a command.
EOF
    echo "   ✅ Created README.md"
fi

# =============================================================================
# tools/ and scripts/ - Development utilities (symlink from proviron)
# =============================================================================
echo ""
echo "📁 Setting up tools/ and scripts/ (development utilities)..."

# Symlink tools/
if [ -d "$PROVIRON_DIR/tools" ]; then
    if [ -L "$SCRIPT_DIR/tools" ]; then
        rm "$SCRIPT_DIR/tools"
    elif [ -d "$SCRIPT_DIR/tools" ]; then
        echo "   ⚠️  Skipping tools/ (local directory exists)"
    fi

    if [ ! -d "$SCRIPT_DIR/tools" ]; then
        ln -s "$PROVIRON_DIR/tools" "$SCRIPT_DIR/tools"
        echo "   ✅ tools/ → proviron"
    fi
else
    echo "   ⚠️  tools/ not found in proviron"
fi

# Symlink scripts/
if [ -d "$PROVIRON_DIR/scripts" ]; then
    if [ -L "$SCRIPT_DIR/scripts" ]; then
        rm "$SCRIPT_DIR/scripts"
    elif [ -d "$SCRIPT_DIR/scripts" ]; then
        echo "   ⚠️  Skipping scripts/ (local directory exists)"
    fi

    if [ ! -d "$SCRIPT_DIR/scripts" ]; then
        ln -s "$PROVIRON_DIR/scripts" "$SCRIPT_DIR/scripts"
        echo "   ✅ scripts/ → proviron"
    fi
else
    echo "   ⚠️  scripts/ not found in proviron"
fi

# =============================================================================
# .crossnote/ - MPE preview styling (symlink from proviron)
# =============================================================================
echo ""
echo "📁 Setting up .crossnote/ (MPE styling)..."

if [ -d "$PROVIRON_DIR/.crossnote" ]; then
    if [ -L "$SCRIPT_DIR/.crossnote" ]; then
        rm "$SCRIPT_DIR/.crossnote"
    elif [ -d "$SCRIPT_DIR/.crossnote" ]; then
        echo "   ⚠️  Skipping .crossnote (local directory exists)"
    fi

    if [ ! -d "$SCRIPT_DIR/.crossnote" ]; then
        ln -s "$PROVIRON_DIR/.crossnote" "$SCRIPT_DIR/.crossnote"
        echo "   ✅ .crossnote → proviron"
    fi
else
    echo "   ⚠️  .crossnote not found in proviron"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Symlinks created. LiveMathTeX now uses proviron's tools and scripts."
echo ""
echo "Note: Cursor rules are available via multi-root workspace."
echo "      Local rules can be added directly to .cursor/rules/ (tracked in git)."
echo ""
echo "To update symlinks after proviron changes:"
echo "  ./setup_symlinks.sh"
echo ""
