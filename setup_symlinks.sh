#!/bin/bash
# setup_symlinks.sh - Setup symlinks to proviron for shared development standards
#
# This script creates symlinks to proviron's:
# - Cursor rules (coding standards, documentation guidelines)
# - Shared tools (optional)
#
# CalcuLaTeX is a standalone project, but during development in the
# axabio workspace, we benefit from shared coding standards.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIRON_DIR="$(dirname "$SCRIPT_DIR")/proviron"

echo "=== CalcuLaTeX Symlink Setup ==="
echo "Script directory: $SCRIPT_DIR"
echo "Proviron directory: $PROVIRON_DIR"
echo ""

# Verify proviron exists
if [ ! -d "$PROVIRON_DIR" ]; then
    echo "⚠️  Proviron not found at $PROVIRON_DIR"
    echo "   This is OK if you're developing CalcuLaTeX standalone."
    echo "   Symlinks will not be created."
    exit 0
fi

# =============================================================================
# .cursor/rules/ - Symlink coding standards from proviron
# =============================================================================
echo "📁 Setting up .cursor/rules/..."

mkdir -p "$SCRIPT_DIR/.cursor/rules"

# Rules to symlink from proviron
RULES_TO_LINK=(
    "general.mdc"
    "general_coding.mdc"
    "general_context.mdc"
    "general_credentials.mdc"
    "documentation.mdc"
    "python.mdc"
)

for rule in "${RULES_TO_LINK[@]}"; do
    SOURCE="$PROVIRON_DIR/.cursor/rules/$rule"
    TARGET="$SCRIPT_DIR/.cursor/rules/$rule"

    if [ -f "$SOURCE" ]; then
        if [ -L "$TARGET" ]; then
            rm "$TARGET"
        elif [ -f "$TARGET" ]; then
            echo "   ⚠️  Skipping $rule (local file exists)"
            continue
        fi
        ln -s "$SOURCE" "$TARGET"
        echo "   ✅ $rule → proviron"
    else
        echo "   ⚠️  $rule not found in proviron"
    fi
done

# Create rules index if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.cursor/rules/index.md" ]; then
    cat > "$SCRIPT_DIR/.cursor/rules/index.md" << 'EOF'
# CalcuLaTeX Cursor Rules

This directory contains Cursor rules for the CalcuLaTeX project.

## Symlinked Rules (from proviron)

General coding standards are symlinked from the proviron repository:
- `general.mdc` - Entry point for always-loaded rules
- `general_coding.mdc` - Coding standards, git workflow
- `general_context.mdc` - Context discovery, search strategies
- `general_credentials.mdc` - Credential storage patterns
- `documentation.mdc` - Markdown documentation standards
- `python.mdc` - Python-specific rules

## Local Rules

CalcuLaTeX-specific rules can be added here as `.mdc` files.
They will override symlinked rules if they have the same name.

## Setup

Run `./setup_symlinks.sh` to create/update symlinks.
EOF
    echo "   ✅ Created index.md"
fi

# =============================================================================
# .cursor/commands/ - CalcuLaTeX specific commands (not symlinked)
# =============================================================================
echo ""
echo "📁 Setting up .cursor/commands/..."
mkdir -p "$SCRIPT_DIR/.cursor/commands"

if [ ! -f "$SCRIPT_DIR/.cursor/commands/README.md" ]; then
    cat > "$SCRIPT_DIR/.cursor/commands/README.md" << 'EOF'
# CalcuLaTeX Cursor Commands

This directory contains Cursor commands specific to CalcuLaTeX development.

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
echo "Symlinks created. CalcuLaTeX now uses proviron's coding standards."
echo ""
echo "To update symlinks after proviron changes:"
echo "  ./setup_symlinks.sh"
echo ""
