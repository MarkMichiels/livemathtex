#!/usr/bin/env python3
"""
Regenerate all example JSON files with IR v3.0 schema.

This script processes all examples/*/input.md files and generates
corresponding input.lmt.json files using the new IR v3.0 schema.
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from livemathtex.core import process_text_v3
from livemathtex.engine.units import reset_unit_registry


def regenerate_all_json():
    """Regenerate all example JSON files with IR v3.0."""
    examples_dir = Path(__file__).parent.parent / "examples"
    
    processed = 0
    errors = []
    
    for example_dir in sorted(examples_dir.iterdir()):
        if not example_dir.is_dir():
            continue
            
        input_file = example_dir / "input.md"
        if not input_file.exists():
            continue
            
        json_file = example_dir / "input.lmt.json"
        
        print(f"Processing {example_dir.name}...")
        
        # Reset unit registry for clean state
        reset_unit_registry()
        
        try:
            # Read and process
            content = input_file.read_text(encoding='utf-8')
            _, ir = process_text_v3(content, source=str(input_file))
            
            # Write JSON
            ir.to_json(json_file)
            
            print(f"  ✓ Generated {json_file.name} (v{ir.version})")
            print(f"    - {len(ir.symbols)} symbols")
            print(f"    - {len(ir.custom_units)} custom units")
            print(f"    - {len(ir.errors)} errors")
            
            processed += 1
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors.append((example_dir.name, str(e)))
    
    print()
    print(f"Processed {processed} examples")
    if errors:
        print(f"Errors: {len(errors)}")
        for name, error in errors:
            print(f"  - {name}: {error}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(regenerate_all_json())
