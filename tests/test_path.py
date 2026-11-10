from pathlib import Path

import pytest

from inqaba import InqPath, InqPathError, InqRelPath


def test_relative_directory_paths_are_not_absolute():
	path = InqRelPath("./People/")
	assert path.value == "People"
	assert path.segments == ("People",)
	assert path.depth == 1


def test_bare_filename_is_the_empty_relative_path():
	assert str(InqRelPath("Person.pit")) == "."


def test_relative_path_rejects_absolute_and_parent_escape():
	with pytest.raises(InqPathError):
		InqRelPath("/tmp/People")
	with pytest.raises(InqPathError):
		InqRelPath("../People")


def test_absolute_path_anchors_relative_directories_and_files():
	root = InqPath.from_directory("~/jsonpit/")
	people = root / InqRelPath("People")
	assert isinstance(people, InqPath)
	assert people.as_path().is_absolute()
	assert people / "Person.pit" == Path(people.as_path() / "Person.pit")
