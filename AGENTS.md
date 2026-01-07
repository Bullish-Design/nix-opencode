# AGENTS.md


# AGENTS.md

```markdown
# AGENTS.md

Guide for creating a NixOS devenv.sh managed flake wrapping the opencode LLM agent application.

## Project Context

This flake will integrate with the Bullish-Design NixOS ecosystem:
- `nixos-core`: System-level NixOS modules
- `nix-terminal`: Terminal environment with zsh, atuin, neovim
- `nix-meta`: Configuration orchestration layer
- `repoman`: Repository management
- `nixbuild`: NixOS rebuild testing
- `nixvim`: Neovim configuration

## Objective

Create a standalone flake that:
1. Uses devenv.sh for reproducible development environments
2. Wraps the opencode LLM agent (GitHub: github.com/AmadeusITGroup/opencode)
3. Provides a clean CLI interface via nixos wrapper
4. Integrates with existing Bullish-Design tooling patterns

## Technical Requirements

### File Structure

```
nix-opencode/
├── devenv.nix          # Development environment configuration
├── devenv.yaml         # Devenv inputs specification
├── flake.nix           # Nix flake definition
├── src/
│   └── opencode_wrapper/
│       ├── __init__.py
│       ├── cli.py      # Typer-based CLI
│       └── wrapper.py  # Opencode integration logic
├── pyproject.toml      # Python project metadata (uv compatible)
└── README.md
```

### Python Specifications

- Python 3.12+
- Use Pydantic for all data models
- Use Typer for CLI (consistent with nixbuild pattern)
- Use `from __future__ import annotations` in all files
- Avoid quoted type hints
- Keep lines under 120 characters
- File header comment: `# src/opencode_wrapper/cli.py`
- UV for dependency management

### devenv.nix Pattern

Reference the repoman pattern:

```nix
{ pkgs, ... }:
{
  env = {
    DEVENV_PROJECT = "opencode-wrapper";
  };

  packages = with pkgs; [
    git
    curl
    jq
  ];

  scripts = {
    # Define helper scripts here
  };

  languages = {
    python = {
      enable = true;
      version = "3.12";
      venv.enable = true;
      uv.enable = true;
    };
  };

  enterShell = ''
    # Welcome message and setup instructions
  '';
}
```

### devenv.yaml Pattern

```yaml
inputs:
  nixpkgs:
    url: github:cachix/devenv-nixpkgs/rolling
  nixpkgs-python:
    url: github:cachix/nixpkgs-python
```

### flake.nix Structure

Must export:
- `packages.${system}.default` - The opencode wrapper as a Python application
- `apps.${system}.default` - Runnable app entry point
- `devShells.${system}.default` - Development shell with all dependencies

Reference nixbuild/flake.nix for Python application packaging pattern.

### Opencode Integration

The wrapper should:
1. Install opencode as a dependency or subprocess call
2. Provide configuration management for opencode settings
3. Offer convenience commands for common workflows
4. Handle errors gracefully with clear messages
5. Support both interactive and non-interactive modes

### CLI Design

Use Typer with subcommands:
```python
app = typer.Typer(help="Opencode LLM agent wrapper")

@app.command()
def run(...) -> None:
    """Execute opencode agent with managed configuration"""

@app.command()
def config(...) -> None:
    """Manage opencode configuration"""
```

## Integration Points

### With nix-terminal
- Should work within nix-terminal zsh environment
- Respect terminal settings and themes
- Use ripgrep/fd for file operations if needed

### With nixbuild
- Could potentially integrate build testing workflows
- Share common patterns (Typer CLI, structured output)

### With repoman
- May need to interact with managed repositories
- Follow similar configuration file patterns (YAML/TOML)

## Configuration Management

Consider supporting:
- `~/.config/opencode-wrapper/config.yaml` for user settings
- Environment variables for API keys/tokens
- Project-level `.opencode.yaml` files
- Validation using Pydantic models

Example config model:
```python
# src/opencode_wrapper/config.py
from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field

class OpencodeConfig(BaseModel):
    """Configuration for opencode wrapper."""
    
    api_key: str | None = None
    model: str = Field(default="gpt-4")
    max_tokens: int = Field(default=4096, ge=1, le=32000)
    workspace_dir: Path = Field(default=Path("~/opencode-workspace"))
```

## Testing Approach

- Use pytest for unit tests
- Test in development shell: `nix develop`
- Validate flake: `nix flake check`
- Build package: `nix build`
- Run directly: `nix run .#`

## Critical Constraints

1. **No breaking of devenv.sh patterns** - Must work with devenv tooling
2. **UV-only for Python dependencies** - No pip, poetry, or other tools
3. **Pydantic for all models** - Data validation and serialization
4. **Typer for CLI** - Consistency with nixbuild
5. **Lines under 120 chars** - Code formatting requirement
6. **Object-based design** - "True Smalltalk OOP" philosophy
7. **No ego-boosting comments** - Keep code comments technical

## Potential Issues to Avoid

- **Don't hardcode paths** - Use XDG base directories or config
- **Don't assume sudo access** - Should work in user space
- **Don't mix package managers** - UV only, no pip install
- **Don't use complex async** - Keep it simple unless necessary
- **Don't skip error handling** - All external calls must handle failures
- **Don't ignore existing patterns** - Study repoman/nixbuild/nixvim

## Expected Deliverables

1. Complete flake.nix with proper outputs
2. Working devenv.nix for development
3. Python package installable via nix
4. CLI accessible via `nix run`
5. README with usage examples
6. Basic configuration system

## Success Criteria

- `nix flake check` passes
- `nix build` produces working package
- `nix run .#` executes CLI
- `nix develop` provides full dev environment
- UV can install dependencies in devshell
- CLI accepts commands and produces output
- Configuration loads from expected locations
- Errors are handled with clear messages

## Reference Commands

```bash
# Development
nix develop
uv pip install -e ./src
opencode-wrapper --help

# Building
nix flake check
nix build
./result/bin/opencode-wrapper

# Running
nix run .# -- run --help
```

## Notes

- This wrapper should feel native to the Bullish-Design ecosystem
- Study the existing repos for patterns - don't reinvent
- Keep it minimal - only wrap what's necessary
- Make it composable - should integrate, not isolate
- Document integration points clearly

## Anti-Patterns to Avoid

Based on existing repo analysis:
- Complex DI containers (see nixbuild v0.2.0 refactoring)
- Over-abstraction (keep it direct)
- Excessive service layers (prefer simple functions)
- Ignoring existing config patterns (YAML/TOML via Pydantic)
- Manual path construction (use Path objects)
- Unvalidated configuration (use Pydantic)

---

This guide should provide sufficient context for an LLM agent to create a well-integrated opencode wrapper that follows established patterns in the Bullish-Design ecosystem.


---



# DevEnv Development Environments

This guide covers setting up reproducible development environments using [devenv](https://devenv.sh/).

## Quick Start

Initialize a new devenv environment:

```bash
nix flake init --template github:cachix/devenv
```

Or manually create `devenv.nix` and `devenv.yaml` in your project root.

## Core Configuration Files

### devenv.yaml

Minimal input configuration:

```yaml
inputs:
  nixpkgs:
    url: github:cachix/devenv-nixpkgs/rolling
```

### devenv.nix

Primary configuration file where all environment setup occurs.

## Python Development

### Python 3.13+ with UV and Virtual Environment

```nix
{ pkgs, lib, config, ... }:

{
  env = {
    PROJECT_NAME = "my-python-project";
  };

  packages = with pkgs; [
    git
    curl
  ];

  languages.python = {
    enable = true;
    version = "3.13";
    venv = {
      enable = true;
    };
    uv = {
      enable = true;
      sync.enable = true;  # Auto-sync on shell entry
    };
  };

  scripts = {
    test = {
      exec = ''
        pytest "$@"
      '';
      description = "Run tests with pytest";
    };

    format = {
      exec = ''
        ruff format src/ tests/
      '';
      description = "Format code with ruff";
    };

    lint = {
      exec = ''
        ruff check src/ tests/
      '';
      description = "Lint code with ruff";
    };

    typecheck = {
      exec = ''
        ty src/
      '';
      description = "Type check with ty typechecker (still in beta, don't rely on it yet)";
    };
  };

  enterShell = ''
    echo "🐍 Python ${config.languages.python.version}"
    echo ""
    echo "Available commands:"
    echo "  test      - Run pytest"
    echo "  format    - Format with ruff"
    echo "  lint      - Lint with ruff"
    echo "  typecheck - Type check with ty"
    echo ""
    echo "Quick start:"
    echo "  uv sync --all-extras"
    echo "  test"
  '';

  # Git hooks
  pre-commit.hooks = {
    ruff = {
      enable = true;
    };
    ruff-format = {
      enable = true;
    };
  };
}
```

### Python with Additional Tools

```nix
{ pkgs, ... }:

{
  packages = with pkgs; [
    # Python tooling
    black
    isort
    mypy
    pytest
    pytest-cov
    
    # Database clients
    postgresql
    redis
    
    # Other tools
    jq
    httpie
  ];

  languages.python = {
    enable = true;
    version = "3.13";
    venv.enable = true;
    uv.enable = true;
    
    # Poetry alternative
    poetry = {
      enable = false;  # Use UV instead
    };
  };
}
```

## JavaScript/TypeScript Development

### Node.js with PNPM

```nix
{ pkgs, ... }:

{
  packages = with pkgs; [
    git
  ];

  languages.javascript = {
    enable = true;
    package = pkgs.nodejs_22;  # LTS version
    
    pnpm = {
      enable = true;
      install.enable = true;  # Auto-install on shell entry
    };
  };

  scripts = {
    dev = {
      exec = ''
        pnpm dev
      '';
      description = "Start development server";
    };

    build = {
      exec = ''
        pnpm build
      '';
      description = "Build for production";
    };

    test = {
      exec = ''
        pnpm test "$@"
      '';
      description = "Run tests";
    };

    lint = {
      exec = ''
        pnpm lint
      '';
      description = "Lint with ESLint";
    };

    typecheck = {
      exec = ''
        pnpm tsc --noEmit
      '';
      description = "Type check with TypeScript";
    };
  };

  enterShell = ''
    echo "📦 Node.js $(node --version)"
    echo "📌 pnpm $(pnpm --version)"
    echo ""
    echo "Available commands:"
    echo "  dev       - Start dev server"
    echo "  build     - Build for production"
    echo "  test      - Run tests"
    echo "  lint      - Lint code"
    echo "  typecheck - Type check"
    echo ""
    if [ ! -d "node_modules" ]; then
      echo "💡 Run 'pnpm install' to install dependencies"
    fi
  '';

  # Git hooks
  pre-commit.hooks = {
    eslint = {
      enable = true;
    };
    prettier = {
      enable = true;
    };
  };
}
```

### TypeScript with Bun

```nix
{ pkgs, ... }:

{
  languages.javascript = {
    enable = true;
    bun = {
      enable = true;
      install.enable = true;
    };
  };

  languages.typescript = {
    enable = true;
  };

  packages = with pkgs; [
    # TypeScript tooling comes with bun
  ];

  scripts = {
    dev = {
      exec = ''
        bun run dev
      '';
      description = "Start development with Bun";
    };

    test = {
      exec = ''
        bun test "$@"
      '';
      description = "Run Bun tests";
    };
  };
}
```

## Git Hooks

### Using pre-commit.hooks

```nix
{ ... }:

{
  pre-commit.hooks = {
    # Formatting
    prettier = {
      enable = true;
      excludes = [ "flake.lock" ];
    };
    
    ruff = {
      enable = true;
    };
    
    # Linting
    eslint = {
      enable = true;
    };
    
    shellcheck = {
      enable = true;
    };
    
    # Nix
    nixpkgs-fmt = {
      enable = true;
    };
    
    # Security
    detect-secrets = {
      enable = true;
    };
    
    # Custom hook
    custom-check = {
      enable = true;
      name = "Custom validation";
      entry = "${pkgs.writeShellScript "custom-check" ''
        #!/usr/bin/env bash
        set -euo pipefail
        echo "Running custom validation..."
        # Your validation logic here
      ''}";
      pass_filenames = false;
    };
  };
}
```

### Manual Git Hook Configuration

```nix
{ pkgs, ... }:

{
  git-hooks.hooks = {
    pre-commit = "${pkgs.writeShellScript "pre-commit" ''
      #!/usr/bin/env bash
      set -euo pipefail
      
      echo "Running pre-commit checks..."
      
      # Format check
      if command -v ruff &> /dev/null; then
        ruff check .
      fi
      
      # Type check
      if command -v mypy &> /dev/null; then
        mypy src/
      fi
    ''}";
  };
}
```

## Services

### PostgreSQL Database

```nix
{ ... }:

{
  services.postgres = {
    enable = true;
    package = pkgs.postgresql_16;
    initialDatabases = [
      { name = "myapp_dev"; }
      { name = "myapp_test"; }
    ];
    initialScript = ''
      CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
      CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    '';
    listen_addresses = "127.0.0.1";
    port = 5432;
  };

  enterShell = ''
    echo "🐘 PostgreSQL running on port 5432"
    echo "   Databases: myapp_dev, myapp_test"
  '';
}
```

### Redis

```nix
{ ... }:

{
  services.redis = {
    enable = true;
    port = 6379;
  };

  enterShell = ''
    echo "🔴 Redis running on port 6379"
  '';
}
```

### Multiple Services

```nix
{ pkgs, ... }:

{
  services = {
    postgres = {
      enable = true;
      initialDatabases = [{ name = "myapp"; }];
    };

    redis = {
      enable = true;
    };

    minio = {
      enable = true;
      port = 9000;
      consolePort = 9001;
    };
  };

  processes = {
    # Background process
    api-server = {
      exec = "uvicorn app.main:app --reload --port 8000";
    };

    # Frontend dev server
    frontend = {
      exec = "cd frontend && pnpm dev";
    };
  };

  enterShell = ''
    echo "🚀 Services started:"
    echo "   PostgreSQL: localhost:5432"
    echo "   Redis: localhost:6379"
    echo "   MinIO: localhost:9000 (console: 9001)"
    echo ""
    echo "🔄 Processes:"
    echo "   API: http://localhost:8000"
    echo "   Frontend: http://localhost:3000"
  '';
}
```

## Advanced Patterns

### Environment-Specific Configuration

```nix
{ pkgs, lib, ... }:

let
  isDevelopment = builtins.getEnv "ENV" == "development";
  isCI = builtins.getEnv "CI" != "";
in
{
  packages = with pkgs; [
    git
  ] ++ lib.optionals isDevelopment [
    # Development-only tools
    ripgrep
    fd
    fzf
  ];

  scripts.ci = lib.mkIf isCI {
    exec = ''
      pytest --cov --cov-report=xml
    '';
    description = "Run CI tests with coverage";
  };
}
```

### Multi-Language Project

```nix
{ pkgs, ... }:

{
  # Backend (Python)
  languages.python = {
    enable = true;
    version = "3.13";
    venv.enable = true;
    uv.enable = true;
  };

  # Frontend (TypeScript)
  languages.javascript = {
    enable = true;
    pnpm.enable = true;
  };

  # Infrastructure (Terraform)
  languages.terraform = {
    enable = true;
  };

  scripts = {
    backend-dev = {
      exec = ''
        cd backend && uvicorn main:app --reload
      '';
      description = "Start backend dev server";
    };

    frontend-dev = {
      exec = ''
        cd frontend && pnpm dev
      '';
      description = "Start frontend dev server";
    };

    deploy = {
      exec = ''
        cd infrastructure && terraform apply
      '';
      description = "Deploy infrastructure";
    };
  };
}
```

### Custom Tasks and Hooks

```nix
{ ... }:

{
  tasks = {
    "project:setup" = {
      exec = ''
        echo "Setting up project..."
        uv sync --all-extras
        pnpm install
        echo "✓ Setup complete"
      '';
    };

    "devenv:enterShell" = {
      after = [ "project:setup" ];
    };
  };

  enterTest = ''
    echo "Running environment tests..."
    python --version | grep "3.13"
    node --version
    pnpm --version
    echo "✓ All checks passed"
  '';
}
```

## Testing the Environment

```bash
# Enter the environment
devenv shell

# Run tests on the environment
nix flake check

# Update inputs
devenv update
```

## Common Patterns from Projects

### Python CLI Tool (from repoman)

```nix
{ pkgs, ... }:

{
  packages = with pkgs; [
    git
    curl
    jq
  ];

  scripts = {
    test = {
      exec = "pytest \"$@\"";
      description = "Run tests with pytest";
    };

    format = {
      exec = "ruff format src/ tests/";
      description = "Format code with ruff";
    };

    lint = {
      exec = "ruff check src/ tests/";
      description = "Lint code with ruff";
    };
  };

  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    uv.enable = true;
  };

  enterShell = ''
    echo "Available commands:"
    echo "  test   - Run tests with pytest"
    echo "  format - Format code with ruff"
    echo "  lint   - Lint code with ruff"
  '';
}
```

## Tips

1. **Keep it minimal**: Only include what you actually need
2. **Use scripts**: Define common commands as scripts for discoverability
3. **Informative enterShell**: Show useful information when entering the shell
4. **Git hooks**: Automate checks to maintain code quality
5. **Services**: Run databases and other services automatically
6. **Version pinning**: Use specific versions for reproducibility

## Resources

- [DevEnv Documentation](https://devenv.sh/)
- [DevEnv Examples](https://github.com/cachix/devenv/tree/main/examples)
- [Supported Languages](https://devenv.sh/languages/)
- [Supported Services](https://devenv.sh/services/)
