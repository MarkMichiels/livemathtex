import click
from pathlib import Path
from .core import process_file
from .config import LivemathConfig
from .parser.lexer import Lexer

@click.group()
def main():
    """Livemathtex CLI - Live mathematical calculations in LaTeX/Markdown."""
    pass

@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help="Output file path")
@click.option('-v', '--verbose', is_flag=True, help="Write IR to JSON file for debugging")
@click.option('--ir-output', type=click.Path(), help="Custom path for IR JSON (default: input.lmt.json)")
def process(input_file, output, verbose, ir_output):
    """Process a markdown file and execute calculations.

    Examples:

        livemathtex process input.md
        livemathtex process input.md -o output.md
        livemathtex process input.md --verbose
        livemathtex process input.md -v --ir-output debug.json

    The --verbose flag can also be enabled via document directive:

        <!-- livemathtex: json=true -->
    """
    try:
        # Check document directive for json
        input_path = Path(input_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lexer = Lexer()
        doc_directives = lexer.parse_document_directives(content)
        config = LivemathConfig.load(input_path).with_overrides(doc_directives)

        # CLI --verbose OR document json=true
        should_generate_ir = verbose or config.json

        ir = process_file(
            input_file,
            output,
            verbose=should_generate_ir,
            ir_output_path=ir_output
        )

        # Show summary
        stats = ir.stats
        click.echo(f"✓ Processed {input_file}")
        click.echo(f"  Symbols: {stats.get('symbols', 0)}")
        click.echo(f"  Definitions (:=): {stats.get('definitions', 0)}")
        click.echo(f"  Evaluations (==): {stats.get('evaluations', 0)}")
        click.echo(f"  Symbolic (=>):    {stats.get('symbolic', 0)}")

        errors = stats.get('errors', 0)
        if errors > 0:
            click.echo(click.style(f"  Errors: {errors}", fg='red'))
        else:
            click.echo(click.style("  Errors: 0", fg='green'))

        click.echo(f"  Duration: {stats.get('duration', 'N/A')}")

        if should_generate_ir:
            ir_path = ir_output or str(Path(input_file).with_suffix('.lmt.json'))
            click.echo(f"  IR written to: {ir_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument('ir_file', type=click.Path(exists=True))
def inspect(ir_file):
    """Inspect a livemathtex IR JSON file (v2.0 schema).

    Shows symbols with their original and SI values.
    """
    from .ir import LivemathIR

    try:
        ir = LivemathIR.from_json(Path(ir_file))

        click.echo(f"Source: {ir.source}")
        click.echo(f"Version: {ir.version}")
        click.echo()

        # Custom units
        if ir.custom_units:
            click.echo("Custom Units:")
            for name, definition in ir.custom_units.items():
                click.echo(f"  {name} = {definition}")
            click.echo()

        # Symbols
        if ir.symbols:
            click.echo("Symbols:")
            for name, entry in ir.symbols.items():
                # Format original value
                orig = entry.original
                orig_str = ""
                if orig.value is not None:
                    orig_str = f"{orig.value}"
                    if orig.unit:
                        orig_str += f" {orig.unit}"

                # Format SI value
                si = entry.si
                si_str = ""
                if si.value is not None:
                    si_str = f"{si.value}"
                    if si.unit:
                        si_str += f" [{si.unit}]"

                # Validation status
                valid_mark = "✓" if entry.valid else "✗"

                # Display
                click.echo(f"  {name}:")
                click.echo(f"    id: {entry.id}")
                if orig_str:
                    click.echo(f"    original: {orig_str}")
                if si_str:
                    click.echo(f"    SI: {si_str}")
                click.echo(f"    valid: {valid_mark}")
            click.echo()

        # Errors
        if ir.errors:
            click.echo(click.style("Errors:", fg='red'))
            for error in ir.errors:
                click.echo(f"  Line {error.line}: {error.message}")
            click.echo()

        # Stats
        if ir.stats:
            click.echo("Stats:")
            for key, value in ir.stats.items():
                click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"Error reading IR file: {e}", err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
