"""Shared configuration discovery and cloud roots for RAIkeep."""
from __future__ import annotations
import os
from typing import Any
from .entry import InqEntry
from .path import InqPath
from .json5 import loads_json5

DEFAULT_CONFIG_FILE_LOCATION: str = "~/.config/RAIkeep.json5"


def missing_configuration_diagnostic() -> str:
	"""
	CR044 §7.4: Standardized diagnostic when RAIkeep configuration is not found.
	Directs the operator to 'amafu init'.
	"""
	return (
		f"RAIkeep configuration was not found at '{DEFAULT_CONFIG_FILE_LOCATION}'. "
		"Run 'amafu init' to detect cloud providers and create it."
	)


class InqConfig:
	"""
	System configuration derived from ~/.config/RAIkeep.json5 or fallback files.
	Provides authoritative cloud drive paths, temporary directories, and backup paths.
	"""

	_instance: InqConfig | None = None

	def __init__(self, config_dict: dict[str, Any] | None = None, config_path: InqEntry | None = None) -> None:
		self._config_path = config_path
		raw = config_dict or {}

		# TempDir
		raw_temp = raw.get("TempDir", "~/temp/")
		self.temp_dir: InqEntry = self._normalize_path(raw_temp)

		# LocalBackupDir
		raw_backup = raw.get("LocalBackupDir")
		self.local_backup_dir: InqEntry | None = self._normalize_path(raw_backup) if raw_backup else None

		# SyncPropagationDelayMs
		self.sync_propagation_delay_ms: int = int(raw.get("SyncPropagationDelayMs", 10000))

		# DefaultCloudOrder
		self.default_cloud_order: list[str] = list(
			raw.get("DefaultCloudOrder", ["OneDrive", "Dropbox", "GoogleDrive", "ICloudDrive"])
		)

		# Cloud roots
		self.clouds: dict[str, InqEntry] = {}
		raw_cloud = raw.get("Cloud", {})
		if isinstance(raw_cloud, dict):
			for name, path_str in raw_cloud.items():
				if path_str:
					self.clouds[name] = self._normalize_path(str(path_str))

	@property
	def is_config_loaded(self) -> bool:
		"""Returns True if configuration was loaded from a file or explicit dictionary."""
		return self._config_path is not None or bool(self.clouds)

	@classmethod
	def reset(cls) -> None:
		"""Resets the singleton instance (used in tests)."""
		cls._instance = None

	@staticmethod
	def _normalize_path(p: str) -> InqEntry:
		expanded = os.path.expanduser(p.strip())
		return InqPath.from_directory(expanded)

	@staticmethod
	def find_config_file() -> InqEntry | None:
		"""Locates the active configuration file according to ecosystem precedence."""
		# 1. Environment variable override
		for env_var in ("JSONPIT_CONFIG", "RAIKEEP_CONFIG"):
			val = os.getenv(env_var)
			if val:
				p = InqEntry(os.path.expanduser(val))
				if p.is_file():
					return p

		# 2. Shared ecosystem ground truth: ~/.config/RAIkeep.json5
		raikeep = InqEntry(os.path.expanduser("~/.config/RAIkeep.json5"))
		if raikeep.is_file():
			return raikeep

		# 3. Python-specific fallback: ~/.config/umgodi.json5
		umgodi_conf = InqEntry(os.path.expanduser("~/.config/umgodi.json5"))
		if umgodi_conf.is_file():
			return umgodi_conf

		# 4. XDG fallback: $XDG_CONFIG_HOME/umgodi/config.json5
		xdg_config = os.getenv("XDG_CONFIG_HOME")
		if xdg_config:
			xdg_path = InqEntry(os.path.expanduser(xdg_config)) / "umgodi" / "config.json5"
			if xdg_path.is_file():
				return xdg_path

		return None

	@classmethod
	def load(cls, config_path: InqEntry | str | None = None) -> InqConfig:
		"""Loads InqConfig from file or singleton instance."""
		if config_path is not None:
			p = InqEntry(os.path.expanduser(str(config_path)))
			if p.is_file():
				data = loads_json5(p.read_text(encoding="utf-8"))
				return cls(data, config_path=p)
			raise FileNotFoundError(f"Configuration file not found: {p}")

		if cls._instance is not None:
			return cls._instance

		resolved_file = cls.find_config_file()
		if resolved_file and resolved_file.is_file():
			try:
				data = loads_json5(resolved_file.read_text(encoding="utf-8"))
				cls._instance = cls(data, config_path=resolved_file)
				return cls._instance
			except Exception:
				pass

		# Fallback default configuration
		cls._instance = cls({}, config_path=None)
		return cls._instance

	def get_cloud_root(self, cloud_name: str | None = None) -> InqEntry | None:
		"""Returns the InqEntry to the requested cloud drive root, or default."""
		if cloud_name:
			# Check case-insensitive match
			for k, v in self.clouds.items():
				if k.lower() == cloud_name.lower():
					return v
			return None
		# Use default cloud order
		for cloud in self.default_cloud_order:
			root = self.get_cloud_root(cloud)
			if root and root.exists():
				return root
		return None

	def is_cloud_path(self, path: InqEntry | str) -> bool:
		"""
		Returns True if the target path is inside any known cloud drive root.
		Resolves symbolic shortcuts and existing ancestors matching CR051.
		"""
		target = InqEntry(os.path.abspath(os.path.expanduser(str(path))))
		try:
			target_resolved = target.resolve()
		except Exception:
			target_resolved = target

		for root in self.clouds.values():
			try:
				root_resolved = root.resolve()
			except Exception:
				root_resolved = root

			for cand in (target, target_resolved):
				for r in (root, root_resolved):
					try:
						cand.relative_to(r)
						return True
					except ValueError:
						continue
		return False
