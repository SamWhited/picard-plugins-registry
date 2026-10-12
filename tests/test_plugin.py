"""Tests for plugin operations."""

from unittest.mock import patch

import pytest

from registry_lib.plugin import (
    add_plugin,
    update_all_plugins,
    update_plugin,
)
from registry_lib.registry import Registry


@pytest.fixture
def temp_registry(tmp_path):
    """Create temporary registry."""
    return Registry(str(tmp_path / "plugins.toml"))


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_basic(mock_fetch, temp_registry):
    """Test adding a basic plugin."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "authors": ["Test Author"],
    }

    plugin = add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    assert plugin["id"] == "test-plugin"
    assert plugin["uuid"] == "6de6a3bf-a524-42b6-83cb-a36b2ec2e246"
    assert plugin["name"] == "Test Plugin"
    assert plugin["trust_level"] == "community"
    assert plugin["authors"] == ["Test Author"]
    assert "added_at" in plugin
    assert "updated_at" in plugin


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_categories(mock_fetch, temp_registry):
    """Test adding plugin with custom categories."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    plugin = add_plugin(
        temp_registry, "https://github.com/user/test-plugin", "community", categories=["metadata", "coverart"]
    )

    assert plugin["categories"] == ["metadata", "coverart"]


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_i18n(mock_fetch, temp_registry):
    """Test adding plugin with translations."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "name_i18n": {"de": "Test Plugin DE"},
        "description_i18n": {"de": "Ein Test Plugin"},
    }

    plugin = add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    assert plugin["name_i18n"] == {"de": "Test Plugin DE"}
    assert plugin["description_i18n"] == {"de": "Ein Test Plugin"}


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_report_bugs_to(mock_fetch, temp_registry):
    """Test adding plugin with report_bugs_to."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "report_bugs_to": "https://github.com/user/test-plugin/issues",
    }

    plugin = add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    assert plugin["report_bugs_to"] == "https://github.com/user/test-plugin/issues"


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_optional_url_fields(mock_fetch, temp_registry):
    """Test adding plugin with license, license_url, and homepage."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "license": "GPL-2.0-or-later",
        "license_url": "https://www.gnu.org/licenses/gpl-2.0.html",
        "homepage": "https://example.com/test-plugin",
    }

    plugin = add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    assert plugin["license"] == "GPL-2.0-or-later"
    assert plugin["license_url"] == "https://www.gnu.org/licenses/gpl-2.0.html"
    assert plugin["homepage"] == "https://example.com/test-plugin"


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_long_description(mock_fetch, temp_registry):
    """Test adding plugin with long_description and long_description_i18n."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "long_description": "This is a longer description of the plugin.",
        "long_description_i18n": {"de": "Dies ist eine längere Beschreibung."},
    }

    plugin = add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    assert plugin["long_description"] == "This is a longer description of the plugin."
    assert plugin["long_description_i18n"] == {"de": "Dies ist eine längere Beschreibung."}


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_with_multi_refs(mock_fetch, temp_registry):
    """Test adding plugin with multiple refs."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    plugin = add_plugin(
        temp_registry, "https://github.com/user/test-plugin", "community", refs="main:4.0,picard-v3:3.0-3.99"
    )

    assert "refs" in plugin
    assert len(plugin["refs"]) == 2
    assert plugin["refs"][0] == {"name": "main", "min_api_version": "4.0"}
    assert plugin["refs"][1] == {"name": "picard-v3", "min_api_version": "3.0", "max_api_version": "3.99"}


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_invalid_trust_level(mock_fetch, temp_registry):
    """Test adding plugin with invalid trust level."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    with pytest.raises(ValueError, match="Invalid trust level"):
        add_plugin(temp_registry, "https://github.com/user/test-plugin", "invalid")


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_duplicate(mock_fetch, temp_registry):
    """Test adding duplicate plugin by URL."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    with pytest.raises(ValueError, match="Plugin with git URL.*already exists"):
        add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_duplicate_uuid(mock_fetch, temp_registry):
    """Test adding plugin with duplicate UUID."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Try to add different plugin with same UUID
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Another Plugin",
        "version": "1.0.0",
        "description": "Another plugin",
        "api": ["3.0"],
    }

    with pytest.raises(ValueError, match="Plugin with UUID.*already exists"):
        add_plugin(temp_registry, "https://github.com/user/another-plugin", "community")


@patch("registry_lib.plugin.fetch_manifest")
def test_add_plugin_duplicate_id(mock_fetch, temp_registry):
    """Test adding plugin with duplicate ID (derived from URL)."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Try to add with different UUID but same derived ID (same URL base)
    mock_fetch.return_value = {
        "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }

    with pytest.raises(ValueError, match="Plugin with ID.*already exists"):
        add_plugin(temp_registry, "https://github.com/user/test-plugin.git", "community")


@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin(mock_fetch, temp_registry):
    """Test updating plugin metadata."""
    # Add plugin first
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Old description",
        "api": ["3.0"],
        "authors": ["Old Author"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Update with new manifest
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin Updated",
        "version": "2.0.0",
        "description": "New description",
        "api": ["3.0"],
        "authors": ["New Author"],
    }

    plugin = update_plugin(temp_registry, "test-plugin")

    assert plugin["name"] == "Test Plugin Updated"
    assert plugin["description"] == "New description"
    assert plugin["authors"] == ["New Author"]
    mock_fetch.assert_called_with("https://github.com/user/test-plugin", "main")


@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin_custom_ref(mock_fetch, temp_registry):
    """Test updating plugin metadata."""
    # Add plugin first
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Old description",
        "api": ["3.0"],
        "authors": ["Old Author"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community", refs="v1:3.0,master")

    update_plugin(temp_registry, "test-plugin")

    mock_fetch.assert_called_with("https://github.com/user/test-plugin", "v1")


@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin_report_bugs_to(mock_fetch, temp_registry):
    """Test that report_bugs_to is synced on update."""
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Update adds report_bugs_to
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.1.0",
        "description": "A test plugin",
        "api": ["3.0"],
        "report_bugs_to": "https://github.com/user/test-plugin/issues",
    }
    plugin = update_plugin(temp_registry, "test-plugin")
    assert plugin["report_bugs_to"] == "https://github.com/user/test-plugin/issues"

    # Update removes report_bugs_to
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.2.0",
        "description": "A test plugin",
        "api": ["3.0"],
    }
    plugin = update_plugin(temp_registry, "test-plugin")
    assert "report_bugs_to" not in plugin


@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin_uuid_changed(mock_fetch, temp_registry):
    """Test that updating plugin with changed UUID raises error."""
    # Add plugin first
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Test description",
        "api": ["3.0"],
        "authors": ["Test Author"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Try to update with different UUID
    mock_fetch.return_value = {
        "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Test description",
        "api": ["3.0"],
        "authors": ["Test Author"],
    }

    with pytest.raises(ValueError, match="UUID mismatch.*UUIDs must not change"):
        update_plugin(temp_registry, "test-plugin")


@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin_invalid_manifest(mock_fetch, temp_registry):
    """Test that updating plugin with invalid manifest raises error."""
    # Add plugin first
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Test description",
        "api": ["3.0"],
        "authors": ["Test Author"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Try to update with invalid manifest (missing required field)
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        # Missing required 'name' field
        "description": "Test description",
        "api": ["3.0"],
    }

    with pytest.raises(ValueError, match="Manifest validation failed.*Missing required field: name"):
        update_plugin(temp_registry, "test-plugin")


@patch("registry_lib.picard.validator.render_markdown")
@patch("registry_lib.plugin.fetch_manifest")
def test_update_plugin_long_description_with_html(mock_fetch, mock_render_markdown, temp_registry):
    """Test that updating plugin with HTML in long_description raises error and calls render_markdown."""
    # Add plugin first
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "Test description",
        "api": ["3.0"],
    }
    add_plugin(temp_registry, "https://github.com/user/test-plugin", "community")

    # Try to update with HTML in long_description
    mock_fetch.return_value = {
        "uuid": "6de6a3bf-a524-42b6-83cb-a36b2ec2e246",
        "name": "Test Plugin",
        "description": "Test description",
        "api": ["3.0"],
        "long_description": "This is a <b>bold</b> description with HTML tags",
    }

    with pytest.raises(ValueError, match="Manifest validation failed.*contains HTML tags"):
        update_plugin(temp_registry, "test-plugin")

    mock_render_markdown.assert_called_once_with(
        "This is a <b>bold</b> description with HTML tags", output_format='html'
    )


def _manifest(uuid, name="Test Plugin", description="A test plugin", version="1.0.0", **extra):
    """Build a minimal valid manifest for tests."""
    manifest = {
        "uuid": uuid,
        "name": name,
        "version": version,
        "description": description,
        "api": ["3.0"],
    }
    manifest.update(extra)
    return manifest


@patch("registry_lib.plugin.fetch_manifest")
def test_update_all_plugins_mixed(mock_fetch, temp_registry):
    """Test update-all reports updated, unchanged, and failed plugins."""
    uuid_a = "6de6a3bf-a524-42b6-83cb-a36b2ec2e246"
    uuid_b = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    uuid_c = "9c5b1d2e-3f4a-4b6c-8d7e-0a1b2c3d4e5f"

    # Add three plugins
    mock_fetch.return_value = _manifest(uuid_a, name="Alpha", description="Old A")
    add_plugin(temp_registry, "https://github.com/user/alpha", "community")
    mock_fetch.return_value = _manifest(uuid_b, name="Bravo", description="B stays")
    add_plugin(temp_registry, "https://github.com/user/bravo", "community")
    mock_fetch.return_value = _manifest(uuid_c, name="Charlie", description="C ok")
    add_plugin(temp_registry, "https://github.com/user/charlie", "community")

    # alpha changes, bravo unchanged, charlie fails (UUID mismatch)
    def fetch_side_effect(git_url, ref):
        if "alpha" in git_url:
            return _manifest(uuid_a, name="Alpha", description="New A")
        if "bravo" in git_url:
            return _manifest(uuid_b, name="Bravo", description="B stays")
        if "charlie" in git_url:
            return _manifest("5d3a7b8c-9e0f-4a1b-8c2d-3e4f5a6b7c8d", name="Charlie")
        raise AssertionError(f"unexpected url {git_url}")

    mock_fetch.side_effect = fetch_side_effect

    results = update_all_plugins(temp_registry)
    by_id = {r["id"]: r for r in results}

    assert by_id["alpha"]["status"] == "updated"
    assert by_id["bravo"]["status"] == "unchanged"
    assert by_id["charlie"]["status"] == "failed"
    assert "UUID mismatch" in by_id["charlie"]["error"]

    # Registry still mutated for alpha, charlie left unchanged despite failure
    assert temp_registry.find_plugin("alpha")["description"] == "New A"
    assert temp_registry.find_plugin("charlie")["name"] == "Charlie"


@patch("registry_lib.plugin.fetch_manifest")
def test_update_all_plugins_empty(mock_fetch, temp_registry):
    """Test update-all on an empty registry returns no results."""
    results = update_all_plugins(temp_registry)
    assert results == []
    mock_fetch.assert_not_called()


@patch("registry_lib.plugin.fetch_manifest")
def test_update_all_plugins_failure_does_not_abort(mock_fetch, temp_registry):
    """Test that a failing plugin does not prevent others from updating."""
    uuid_a = "6de6a3bf-a524-42b6-83cb-a36b2ec2e246"
    uuid_b = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

    mock_fetch.return_value = _manifest(uuid_a, name="Alpha", description="Old A")
    add_plugin(temp_registry, "https://github.com/user/alpha", "community")
    mock_fetch.return_value = _manifest(uuid_b, name="Bravo", description="Old B")
    add_plugin(temp_registry, "https://github.com/user/bravo", "community")

    def fetch_side_effect(git_url, ref):
        if "alpha" in git_url:
            raise ValueError("network error")
        return _manifest(uuid_b, name="Bravo", description="New B")

    mock_fetch.side_effect = fetch_side_effect

    results = update_all_plugins(temp_registry)
    by_id = {r["id"]: r for r in results}

    assert by_id["alpha"]["status"] == "failed"
    assert by_id["bravo"]["status"] == "updated"
    assert temp_registry.find_plugin("bravo")["description"] == "New B"
