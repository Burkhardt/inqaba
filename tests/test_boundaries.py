from pathlib import Path

import pytest

from inqaba import InqConfig, InqFile, InqPath, InqPathError, InqRelPath, InqTextFile
from inqaba.json5 import loads_json5


def test_json5_preserves_comments_inside_strings():
	assert loads_json5("{url: 'https://example.org/a//b', /* real comment */ value: '/*text*/',}") == {
		"url": "https://example.org/a//b", "value": "/*text*/",
	}


@pytest.mark.parametrize("text", ["{} garbage", "{a: @}", "[1", "{a: 'unterminated}"])
def test_malformed_json5_is_rejected(text):
	with pytest.raises(ValueError): loads_json5(text)


@pytest.mark.parametrize("name", ["../outside", "/outside", "a/b", "a\\b", "..", ""])
def test_file_names_cannot_replace_the_parent(tmp_path, name):
	with pytest.raises(InqPathError): InqFile(InqPath(tmp_path), name)


def test_directory_enumeration_keeps_types_and_pathlike_interop(tmp_path):
	root = InqPath(tmp_path)
	directory = root / InqRelPath("child/")
	directory.mkdir()
	file = root / "state.pit"
	assert isinstance(file, InqFile)
	file.write_text("before")
	assert Path(file).read_text() == "before"
	assert {type(p) for p in root.iterdir()} == {InqPath, InqFile}
	assert list(root.glob("*.pit")) == [file]
	assert file.parent == root
	assert str(InqRelPath("directory.with.dots/")) == "directory.with.dots"


def test_durable_write_keeps_inode_and_backup(tmp_path):
	file = InqTextFile(tmp_path / "data.pit")
	file.write_durable("old")
	inode = file.stat().st_ino
	backup = file.copy_to(tmp_path / "backup")
	file.write_durable("new")
	assert file.stat().st_ino == inode
	assert backup.read_text() == "old"
	assert file.read_text() == "new"


def test_cloud_detection_respects_components_and_symlinks(tmp_path):
	cloud = tmp_path / "cloud"
	cloud.mkdir()
	alias = tmp_path / "alias"
	alias.symlink_to(cloud, target_is_directory=True)
	config = InqConfig({"Cloud": {"OneDrive": str(cloud)}})
	assert isinstance(config.get_cloud_root("onedrive"), InqPath)
	assert config.is_cloud_path(alias / "new.pit")
	assert not config.is_cloud_path(tmp_path / "cloud-other" / "new.pit")


def test_default_cloud_skips_unavailable_roots(tmp_path):
	available = tmp_path / "available"
	available.mkdir()
	config = InqConfig({"Cloud": {"OneDrive": str(tmp_path / "missing"), "Dropbox": str(available)}})
	assert config.get_cloud_root() == available
