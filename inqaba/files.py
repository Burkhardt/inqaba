"""Controlled file boundaries built on InqPath."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .path import InqPath


@dataclass(frozen=True, slots=True)
class InqFile:
	parent: InqPath
	name: str

	def as_path(self) -> Path:
		return self.parent.as_path() / self.name

	@property
	def full_name(self) -> str:
		return str(self.as_path())

	def exists(self) -> bool:
		return self.as_path().is_file()

	def delete(self) -> None:
		self.as_path().unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class InqTextFile(InqFile):
	def read_text(self, encoding: str = "utf-8") -> str:
		return self.as_path().read_text(encoding=encoding)

	def write_text(self, content: str, encoding: str = "utf-8") -> None:
		self.as_path().write_text(content, encoding=encoding)


@dataclass(frozen=True, slots=True)
class InqJsonFile(InqTextFile):
	def read_json(self, encoding: str = "utf-8") -> object:
		return json.loads(self.read_text(encoding))

	def write_json(self, value: object, encoding: str = "utf-8") -> None:
		self.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding)
