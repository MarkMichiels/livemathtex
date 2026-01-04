import click
from .core import process_file

@click.group()
def main():
    """Livemathtex CLI"""
    pass

@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help="Output file path")
def process(input_file, output):
    """Process a markdown file and execute calculations."""
    try:
        process_file(input_file, output)
        click.echo(f"Successfully processed {input_file}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    main()
