import pytest
from inqaba import InqConfig


def test_roles_preserve_preference_and_optional_test(tmp_path):
	config = InqConfig({"DefaultCloudOrder": ["OneDrive", "Dropbox"], "Cloud": {"OneDrive": str(tmp_path)}})
	assert config.live_cloud == "OneDrive"
	assert config.test_cloud is None
	assert config.cloud_root("OneDrive").as_path() == tmp_path
	with pytest.raises(ValueError, match="Cloud.Missing"):
		config.cloud_root("Missing")


@pytest.mark.parametrize("key", ["LiveCloud", "TestCloud"])
def test_unknown_roles_fail_during_load(tmp_path, monkeypatch, key):
	config_file = tmp_path / "config.json5"
	config_file.write_text('{Cloud:{OneDrive:"/live/"},' + key + ':"/wrong/path/"}')
	monkeypatch.setenv("RAIKEEP_CONFIG", str(config_file))
	monkeypatch.delenv("JSONPIT_CONFIG", raising=False)
	InqConfig.reset()
	try:
		with pytest.raises(ValueError, match=key + ".*OneDrive"):
			InqConfig.load()
	finally:
		InqConfig.reset()
