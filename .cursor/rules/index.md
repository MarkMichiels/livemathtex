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
