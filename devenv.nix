{ pkgs, config, ... }:

{
  env = {
    PROJECT_NAME = "opencode";
  };

  packages = with pkgs; [
    git
    curl
    jq
  ];

  languages.python = {
    enable = true;
    version = "3.13";
    venv.enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  languages.javascript = {
    enable = true;
    package = pkgs.nodejs_22;
    pnpm = {
      enable = true;
      install.enable = true;
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
    echo "📦 Node.js $(node --version)"
    echo "📌 pnpm $(pnpm --version)"
    echo ""
    echo "Available commands:"
    echo "  test   - Run pytest"
    echo "  format - Format with ruff"
    echo "  lint   - Lint with ruff"
    echo ""
    echo "Quick start:"
    echo "  uv sync --all-extras"
    echo "  test"
  '';

  pre-commit.hooks = {
    ruff.enable = true;
    ruff-format.enable = true;
    nixpkgs-fmt.enable = true;
  };
}
