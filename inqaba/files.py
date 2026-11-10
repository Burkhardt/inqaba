"""File objects keep filesystem access inside Inqaba."""
import json
from pathlib import Path
from .entry import InqEntry
from .path import InqPathError


class InqFile(InqEntry):
	def __init__(self, parent, name=None):
		if name is None:
			super().__init__(parent)
		else:
			if not name or name in (".", "..") or "/" in name or "\\" in name or Path(name).is_absolute():
				raise InqPathError("a file name must be a single terminal name")
			super().__init__(Path(parent) / name)

	@property
	def full_name(self): return str(self)
	def delete(self): self.unlink(missing_ok=True)


class InqTextFile(InqFile):
	"""UTF-8 text file; durable writes preserve the existing inode."""


class InqJsonFile(InqTextFile):
	def read_json(self, encoding="utf-8"):
		return json.loads(self.read_text(encoding=encoding))

	def write_json(self, value, encoding="utf-8"):
		self.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding=encoding)
