import sys
import click


@click.command()
def main(args=None):
    click.echo("test output")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
