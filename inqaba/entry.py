"""PathLike interoperability for inputs whose file/directory kind is not yet known.

InqEntry deliberately exposes an explicit, bounded API rather than forwarding
arbitrary pathlib attributes. Domain code uses InqPath and InqFile once known.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


class InqEntry(os.PathLike[str]):
	def __init__(self, value="."):
		self._native = Path(value)

	def as_path(self):
		return self._native

	def as_posix(self):
		return self._native.as_posix()

	def __fspath__(self):
		return str(self._native)

	def __str__(self):
		return str(self._native)

	def __hash__(self):
		return hash(self._native)

	def __eq__(self, other):
		if not isinstance(other, os.PathLike):
			return NotImplemented
		return self._native == Path(other)

	def __lt__(self, other):
		return self._native < Path(other)

	@classmethod
	def cwd(cls):
		from .path import InqPath
		return InqPath.from_directory(Path.cwd())

	@property
	def parent(self):
		from .path import InqPath
		return InqPath.from_directory(self._native.parent)

	@property
	def parents(self):
		from .path import InqPath
		return tuple(InqPath.from_directory(p) for p in self._native.parents)

	@property
	def name(self): return self._native.name
	@property
	def stem(self): return self._native.stem
	@property
	def suffix(self): return self._native.suffix
	@property
	def parts(self): return self._native.parts

	def __truediv__(self, other):
		return InqEntry(self._native / os.fspath(other))

	def expanduser(self): return type(self)(self._native.expanduser())
	def absolute(self): return type(self)(self._native.absolute())
	def resolve(self, strict=False): return type(self)(self._native.resolve(strict=strict))
	def is_absolute(self): return self._native.is_absolute()
	def relative_to(self, other): return InqEntry(self._native.relative_to(other))
	def with_suffix(self, suffix):
		from .files import InqFile
		return InqFile(self._native.with_suffix(suffix))
	def exists(self): return self._native.exists()
	def is_file(self): return self._native.is_file()
	def is_dir(self): return self._native.is_dir()
	def stat(self): return self._native.stat()
	def mkdir(self, mode=0o777, parents=False, exist_ok=False):
		self._native.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
	def unlink(self, missing_ok=False): self._native.unlink(missing_ok=missing_ok)
	def rename(self, target): return InqEntry(self._native.rename(target))
	def replace(self, target): return InqEntry(self._native.replace(target))
	def open(self, *args, **kwargs): return self._native.open(*args, **kwargs)
	def read_text(self, encoding="utf-8", **kwargs): return self._native.read_text(encoding=encoding, **kwargs)
	def write_text(self, content, encoding="utf-8", **kwargs): return self._native.write_text(content, encoding=encoding, **kwargs)
	def read_bytes(self): return self._native.read_bytes()
	def write_bytes(self, content): return self._native.write_bytes(content)

	@staticmethod
	def _typed(path):
		from .path import InqPath
		from .files import InqFile
		return InqPath.from_directory(path) if path.is_dir() else InqFile(path)

	def iterdir(self):
		return (self._typed(p) for p in self._native.iterdir())

	def glob(self, pattern):
		return (self._typed(p) for p in self._native.glob(pattern))

	def copy_to(self, target):
		return InqEntry(shutil.copy2(self._native, target))

	def write_durable(self, content):
		with self.open("w", encoding="utf-8", newline="") as stream:
			stream.write(content)
			stream.flush()
			os.fsync(stream.fileno())
