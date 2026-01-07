from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence

from pydantic import BaseModel, ConfigDict

from opencode_wrapper.config import OpencodeConfig


class RunResult(BaseModel):
    """Result of running the opencode command."""

    returncode: int
    stdout: str | None = None
    stderr: str | None = None


class CommandSpec(BaseModel):
    """Command metadata for running opencode."""

    model_config = ConfigDict(frozen=True)

    executable: str = "opencode"


class OpencodeRunner:
    """Run the opencode CLI with managed configuration."""

    def __init__(self, command: CommandSpec | None = None) -> None:
        self.command = command or CommandSpec()

    def run(
        self,
        config: OpencodeConfig,
        args: Sequence[str],
        interactive: bool,
        working_dir: Path | None = None,
    ) -> RunResult:
        command = [self.command.executable, *args]
        env = self._build_env(config)
        try:
            if interactive:
                completed = subprocess.run(command, env=env, cwd=working_dir, check=False)
                return RunResult(returncode=completed.returncode)
            completed = subprocess.run(
                command,
                env=env,
                cwd=working_dir,
                check=False,
                text=True,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("opencode executable not found in PATH") from exc
        return RunResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def _build_env(self, config: OpencodeConfig) -> dict[str, str]:
        env = os.environ.copy()
        if config.api_key:
            env["OPENENCODE_API_KEY"] = config.api_key
        env["OPENENCODE_MODEL"] = config.model
        env["OPENENCODE_MAX_TOKENS"] = str(config.max_tokens)
        env["OPENENCODE_WORKSPACE_DIR"] = str(config.workspace_dir)
        return env
