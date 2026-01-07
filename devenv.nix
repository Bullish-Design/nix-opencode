{ pkgs, config, ... }:

{
  env = {
    DEVENV_PROJECT = "opencode-wrapper";
  };

  packages = with pkgs; [
    git
    curl
    jq
    ruff
    pytest
  ];

  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = true;
    uv.enable = true;
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
        ruff format .
      '';
      description = "Format code with ruff";
    };

    lint = {
      exec = ''
        ruff check .
      '';
      description = "Lint code with ruff";
    };
  };

  enterShell = ''
    echo "🐍 Python ${config.languages.python.version}"
    echo ""
    echo "Available commands:"
    echo "  test   - Run pytest"
    echo "  format - Format with ruff"
    echo "  lint   - Lint with ruff"
    echo ""
    echo "Quick start:"
    echo "  uv sync"
    echo "  test"
  '';

  pre-commit.hooks = {
    ruff.enable = true;
    ruff-format.enable = true;
    nixpkgs-fmt.enable = true;
  };
}
