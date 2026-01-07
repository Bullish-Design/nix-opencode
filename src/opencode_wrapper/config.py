from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator
from platformdirs import user_config_path


class OpencodeConfig(BaseModel):
    """Configuration for the opencode wrapper."""

    model_config = ConfigDict(extra="ignore")

    api_key: str | None = None
    model: str = Field(default="gpt-4")
    max_tokens: int = Field(default=4096, ge=1, le=32000)
    workspace_dir: Path = Field(default=Path("~/opencode-workspace"))

    @field_validator("workspace_dir", mode="before")
    @classmethod
    def expand_workspace_dir(cls, value: Any) -> Path:
        path = Path(value).expanduser()
        return path


class ConfigPaths(BaseModel):
    """Resolved configuration locations."""

    user_config_dir: Path
    user_config_file: Path
    project_config_file: Path


class ConfigSource(BaseModel):
    """Information about a configuration source."""

    path: Path
    exists: bool
    loaded: bool
    data: dict[str, Any] = Field(default_factory=dict)


class ConfigLoadResult(BaseModel):
    """Loaded configuration with source metadata."""

    config: OpencodeConfig
    sources: list[ConfigSource]


class ConfigError(RuntimeError):
    """Raised when configuration cannot be loaded or saved."""


class ConfigManager:
    """Manage opencode wrapper configuration files."""

    def __init__(self, app_name: str = "opencode-wrapper", project_file: str = ".opencode.yaml") -> None:
        self.app_name = app_name
        self.project_file = project_file

    def resolve_paths(self, cwd: Path | None = None) -> ConfigPaths:
        root = user_config_path(self.app_name, ensure_exists=False)
        user_config_dir = Path(root)
        user_config_file = user_config_dir / "config.yaml"
        project_root = cwd or Path.cwd()
        project_config_file = project_root / self.project_file
        return ConfigPaths(
            user_config_dir=user_config_dir,
            user_config_file=user_config_file,
            project_config_file=project_config_file,
        )

    def load(self, cwd: Path | None = None) -> ConfigLoadResult:
        paths = self.resolve_paths(cwd)
        sources = []

        user_data = self._read_yaml(paths.user_config_file)
        sources.append(
            ConfigSource(
                path=paths.user_config_file,
                exists=paths.user_config_file.exists(),
                loaded=bool(user_data),
                data=user_data,
            )
        )

        project_data = self._read_yaml(paths.project_config_file)
        sources.append(
            ConfigSource(
                path=paths.project_config_file,
                exists=paths.project_config_file.exists(),
                loaded=bool(project_data),
                data=project_data,
            )
        )

        env_data = self._read_env()
        merged = {**user_data, **project_data, **env_data}
        config = OpencodeConfig.model_validate(merged)
        return ConfigLoadResult(config=config, sources=sources)

    def write_default(self, force: bool = False) -> Path:
        paths = self.resolve_paths()
        if paths.user_config_file.exists() and not force:
            return paths.user_config_file
        paths.user_config_dir.mkdir(parents=True, exist_ok=True)
        default_config = OpencodeConfig().model_dump(mode="json")
        self._write_yaml(paths.user_config_file, default_config)
        return paths.user_config_file

    def _read_env(self) -> dict[str, Any]:
        env_map: dict[str, Any] = {}
        api_key = os.getenv("OPENENCODE_API_KEY")
        if api_key:
            env_map["api_key"] = api_key
        model = os.getenv("OPENENCODE_MODEL")
        if model:
            env_map["model"] = model
        max_tokens = os.getenv("OPENENCODE_MAX_TOKENS")
        if max_tokens:
            try:
                env_map["max_tokens"] = int(max_tokens)
            except ValueError as exc:
                raise ConfigError("OPENENCODE_MAX_TOKENS must be an integer") from exc
        workspace_dir = os.getenv("OPENENCODE_WORKSPACE_DIR")
        if workspace_dir:
            env_map["workspace_dir"] = workspace_dir
        return env_map

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {path}") from exc
        if not isinstance(data, dict):
            raise ConfigError(f"Config file {path} must contain a mapping")
        return data

    def _write_yaml(self, path: Path, data: dict[str, Any]) -> None:
        try:
            path.write_text(yaml.safe_dump(data, sort_keys=False))
        except OSError as exc:
            raise ConfigError(f"Unable to write config to {path}") from exc
