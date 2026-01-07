# src/opencode_wrapper/cli.py
from __future__ import annotations

import typer
import yaml

from opencode_wrapper.config import ConfigError, ConfigManager
from opencode_wrapper.wrapper import OpencodeRunner

app = typer.Typer(help="Opencode LLM agent wrapper")
config_app = typer.Typer(help="Manage opencode wrapper configuration")
app.add_typer(config_app, name="config")


@app.command()
def run(
    args: list[str] = typer.Argument(None, help="Arguments passed through to opencode"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Capture output instead of streaming"),
) -> None:
    """Execute opencode agent with managed configuration."""
    manager = ConfigManager()
    try:
        load_result = manager.load()
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    runner = OpencodeRunner()
    try:
        result = runner.run(load_result.config, args or [], interactive=not non_interactive)
    except RuntimeError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    if result.stdout:
        typer.echo(result.stdout, nl=False)
    if result.stderr:
        typer.echo(result.stderr, nl=False, err=True)
    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


@config_app.command("show")
def config_show() -> None:
    """Show the merged configuration and source locations."""
    manager = ConfigManager()
    try:
        load_result = manager.load()
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    payload = {
        "config": load_result.config.model_dump(mode="json"),
        "sources": [source.model_dump(mode="json") for source in load_result.sources],
    }
    typer.echo(yaml.safe_dump(payload, sort_keys=False))


@config_app.command("init")
def config_init(
    force: bool = typer.Option(False, "--force", help="Overwrite any existing user config"),
) -> None:
    """Create a default user configuration file."""
    manager = ConfigManager()
    try:
        path = manager.write_default(force=force)
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    typer.secho(f"Wrote configuration to {path}", fg=typer.colors.GREEN)


@config_app.command("path")
def config_path() -> None:
    """Show the active configuration paths."""
    manager = ConfigManager()
    paths = manager.resolve_paths()
    typer.echo(f"User config: {paths.user_config_file}")
    typer.echo(f"Project config: {paths.project_config_file}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
