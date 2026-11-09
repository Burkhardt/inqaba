"""Shared Python framework boundaries for RAIkeep."""

from .files import InqFile, InqJsonFile, InqTextFile
from .config import DEFAULT_CONFIG_FILE_LOCATION, InqConfig
from .path import InqPath, InqPathError, InqRelPath

__version__ = "0.1.0"

__all__ = [
	"InqFile",
	"InqConfig",
	"InqJsonFile",
	"InqPath",
	"InqPathError",
	"InqRelPath",
	"InqTextFile",
	"DEFAULT_CONFIG_FILE_LOCATION",
]
