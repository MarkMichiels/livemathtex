# LiveMathTeX Cursor Rules

This directory contains Cursor rules for the LiveMathTeX project.

## Symlinked Rules (from proviron)

General coding standards are symlinked from the proviron repository:
- `general.mdc` - Entry point for always-loaded rules
- `general_coding.mdc` - Coding standards, git workflow
- `general_context.mdc` - Context discovery, search strategies
- `general_credentials.mdc` - Credential storage patterns
- `documentation.mdc` - Markdown documentation standards
- `python.mdc` - Python-specific rules

## Local Rules

LiveMathTeX-specific rules can be added here as `.mdc` files.
They will override symlinked rules if they have the same name.

## Setup

Run `./setup_symlinks.sh` to create/update symlinks.
