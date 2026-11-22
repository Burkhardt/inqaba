import pytest
from inqaba import InqConfig


def test_roles_resolve_configured_provider(configured_test_cloud):
	provider, root = configured_test_cloud
	config = InqConfig.load()
	assert config.test_cloud == provider
	assert config.cloud_root(provider).as_path() == root
	with pytest.raises(ValueError, match="not configured"):
		config.cloud_root("Missing-" + provider)


def test_default_cloud_follows_available_configured_order(configured_test_cloud):
	config = InqConfig.load()
	expected = next((config.clouds[name] for name in config.default_cloud_order
		if name in config.clouds and config.clouds[name].is_dir()), None)
	assert config.get_cloud_root() == expected
