"""Typed absolute and relative directory paths for the RAIkeep Python stack."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class InqPathError(ValueError):
	"""Raised when a path violates the Inqaba path contract."""


def _text(value: str | os.PathLike[str]) -> str:
	value = os.fspath(value)
	if not isinstance(value, str):
		raise TypeError("path values must be text")
	return value.strip()


@dataclass(frozen=True, slots=True)
class InqRelPath(os.PathLike[str]):
	"""Relative directory path; filenames are intentionally not represented here."""

	value: str = ""

	def __post_init__(self) -> None:
		raw = _text(self.value).replace("\\", os.sep)
		if raw in ("", "."):
			object.__setattr__(self, "value", "")
			return
		if os.path.isabs(raw) or (len(raw) > 1 and raw[1] == ":"):
			raise InqPathError("InqRelPath requires a relative path")
		if raw.endswith(os.sep):
			raw = raw.rstrip(os.sep)
		# A terminal filename is not a relative directory path. Match the
		# OsLib split convention: constructing a relative path from a bare
		# filename yields the empty path (displayed as '.').
		if os.sep not in raw and Path(raw).suffix:
			object.__setattr__(self, "value", "")
			return
		parts = [part for part in raw.split(os.sep) if part not in ("", ".")]
		if any(part == ".." for part in parts):
			raise InqPathError("InqRelPath cannot escape its anchor")
		object.__setattr__(self, "value", os.sep.join(parts))

	def __fspath__(self) -> str:
		return self.value

	def __str__(self) -> str:
		return self.value or "."

	@property
	def segments(self) -> tuple[str, ...]:
		return tuple(self.value.split(os.sep)) if self.value else ()

	@property
	def depth(self) -> int:
		return len(self.segments)

	def __truediv__(self, other: str | "InqRelPath") -> "InqRelPath":
		if isinstance(other, InqRelPath):
			part = other.value
		else:
			part = _text(other)
			if os.path.basename(part) != part or part.endswith((".pit", ".json", ".txt")):
				raise InqPathError("filenames belong at an anchored path, not InqRelPath")
		return InqRelPath(os.path.join(self.value, part))


@dataclass(frozen=True, slots=True)
class InqPath(os.PathLike[str]):
	"""Absolute directory path with safe relative composition."""

	_native: Path

	def __post_init__(self) -> None:
		path = self._native.expanduser()
		if not path.is_absolute():
			path = Path.cwd() / path
		object.__setattr__(self, "_native", Path(os.path.abspath(path)))

	@classmethod
	def from_directory(cls, value: str | os.PathLike[str] | Path) -> "InqPath":
		return cls(Path(_text(value)))

	@classmethod
	def from_path(cls, value: str | os.PathLike[str] | Path) -> "InqPath":
		return cls(Path(_text(value)))

	def __fspath__(self) -> str:
		return str(self._native)

	def __str__(self) -> str:
		return str(self._native)

	def as_path(self) -> Path:
		return self._native

	@property
	def segments(self) -> tuple[str, ...]:
		return self._native.parts

	@property
	def depth(self) -> int:
		return len(self.segments)

	def __truediv__(self, other: str | InqRelPath) -> "InqPath | Path":
		if isinstance(other, InqRelPath):
			return InqPath(self._native / other.value)
		name = _text(other)
		if not name or os.path.basename(name) != name:
			raise InqPathError("path composition accepts one relative segment or filename")
		return self._native / name
