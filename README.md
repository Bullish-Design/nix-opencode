# nix-opencode

NixOpenCode is a NixOS flake that wraps the opencode LLM agent with a reproducible devenv.sh environment and
provides a small Typer-based CLI wrapper.

## Quick start

```bash
# Enter the development shell
nix develop

# Sync Python dependencies in the dev shell
uv sync

# Run the wrapper CLI
opencode-wrapper --help

# Run through nix directly
nix run .# -- run --help
```

## Configuration

The wrapper loads configuration from:

1. `~/.config/opencode-wrapper/config.yaml`
2. `.opencode.yaml` in the current project directory
3. Environment variables (highest priority)

Initialize a default user config:

```bash
opencode-wrapper config init
```

Show the merged configuration:

```bash
opencode-wrapper config show
```

## Updating the opencode version

Edit `flake.nix` and update the `opencode-src` input to the desired git ref. For example:

```nix
opencode-src = {
  url = "github:AmadeusITGroup/opencode?ref=main";
  flake = false;
};
```
