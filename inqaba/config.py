"""Shared RAIkeep configuration boundary, equivalent to Os.Config/OsConfig."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .path import InqPath

DEFAULT_CONFIG_FILE_LOCATION = "~/.config/RAIkeep.json5"


def _loads_json5(text: str) -> dict[str, Any]:
	text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
	text = re.sub(r",\s*([}\]])", r"\1", text)
	text = re.sub(r"([,{]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', text)
	return json.loads(text)


class InqConfig:
	"""Process-wide configured roots and OS paths for Inqaba consumers."""

	_instance: "InqConfig | None" = None

	def __init__(self, values: dict[str, Any] | None = None, config_path: Path | None = None):
		values = values or {}
		self.config_path = config_path
		self.temp_dir = InqPath.from_directory(values.get("TempDir", "~/temp/"))
		backup = values.get("LocalBackupDir")
		self.local_backup_dir = InqPath.from_directory(backup) if backup else None
		self.sync_propagation_delay_ms = int(values.get("SyncPropagationDelayMs", 10000))
		self.default_cloud_order = tuple(values.get("DefaultCloudOrder", ("OneDrive", "Dropbox", "GoogleDrive", "ICloudDrive")))
		self.clouds: dict[str, InqPath] = {
			name: InqPath.from_directory(path)
			for name, path in values.get("Cloud", {}).items()
			if path
		}

	@property
	def is_config_loaded(self) -> bool:
		return self.config_path is not None or bool(self.clouds)

	@classmethod
	def reset(cls) -> None:
		cls._instance = None

	@classmethod
	def find_config_file(cls) -> Path | None:
		for variable in ("RAIKEEP_CONFIG", "JSONPIT_CONFIG"):
			value = os.getenv(variable)
			if value and Path(value).expanduser().is_file():
				return Path(value).expanduser()
		candidates = [
			Path("~/.config/RAIkeep.json5").expanduser(),
			Path("~/.config/jsonpit.json5").expanduser(),
		]
		xdg = os.getenv("XDG_CONFIG_HOME")
		if xdg:
			candidates.append(Path(xdg).expanduser() / "jsonpit" / "config.json5")
		return next((path for path in candidates if path.is_file()), None)

	@classmethod
	def load(cls, config_path: str | os.PathLike[str] | None = None) -> "InqConfig":
		if config_path is not None:
			path = Path(config_path).expanduser()
			if not path.is_file():
				raise FileNotFoundError(f"Configuration file not found: {path}")
			return cls(_loads_json5(path.read_text(encoding="utf-8")), path)
		if cls._instance is None:
			path = cls.find_config_file()
			cls._instance = cls(_loads_json5(path.read_text(encoding="utf-8")), path) if path else cls()
		return cls._instance

	def get_cloud_root(self, cloud_name: str | None = None) -> InqPath | None:
		if cloud_name:
			return next((root for name, root in self.clouds.items() if name.lower() == cloud_name.lower()), None)
		return next((root for name in self.default_cloud_order if (root := self.get_cloud_root(name))), None)

	def is_cloud_path(self, path: str | os.PathLike[str]) -> bool:
		target = Path(path).expanduser().resolve()
		return any(root.as_path().resolve() in (target, *target.parents) for root in self.clouds.values())
