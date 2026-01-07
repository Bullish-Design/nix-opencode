{
  description = "NixOpenCode devenv-powered environment for the opencode wrapper";

  inputs = {
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    devenv.url = "github:cachix/devenv";
    flake-utils.url = "github:numtide/flake-utils";
    opencode-src = {
      url = "github:AmadeusITGroup/opencode?ref=main";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, devenv, flake-utils, opencode-src, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pythonPackages = python.pkgs;

        opencode = pythonPackages.buildPythonPackage {
          pname = "opencode";
          version = "main";
          src = opencode-src;
          pyproject = true;
          nativeBuildInputs = [ pythonPackages.setuptools pythonPackages.wheel ];
          doCheck = false;
        };

        opencode-wrapper = pythonPackages.buildPythonApplication {
          pname = "opencode-wrapper";
          version = "0.1.0";
          src = ./.;
          pyproject = true;
          nativeBuildInputs = [ pythonPackages.setuptools pythonPackages.wheel ];
          propagatedBuildInputs = [
            pythonPackages.typer
            pythonPackages.pydantic
            pythonPackages.pyyaml
            pythonPackages.platformdirs
            opencode
          ];
          doCheck = false;
        };
      in
      {
        packages.default = opencode-wrapper;
        apps.default = flake-utils.lib.mkApp { drv = opencode-wrapper; };
        devShells.default = devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [ ./devenv.nix ];
        };
      });
}
