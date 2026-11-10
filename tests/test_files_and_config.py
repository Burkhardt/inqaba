
from inqaba import InqConfig, InqJsonFile, InqPath, InqTextFile


def test_text_and_json_files(tmp_path):
	root = InqPath.from_directory(tmp_path)
	text = InqTextFile(root, "notes.txt")
	text.write_text("hello")
	assert text.read_text() == "hello"

	data = InqJsonFile(root, "state.json")
	data.write_json({"Status": "Ready"})
	assert data.read_json() == {"Status": "Ready"}


def test_config_loads_json5_and_returns_inq_paths(tmp_path):
	config_file = tmp_path / "RAIkeep.json5"
	config_file.write_text(
		"{ Cloud: { OneDrive: '~/OneDrive/' }, TempDir: '~/tmp/', }",
		encoding="utf-8",
	)
	config = InqConfig.load(config_file)
	assert config.temp_dir.as_path().is_absolute()
	assert config.get_cloud_root("onedrive") is not None
