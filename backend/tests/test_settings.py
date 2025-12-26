from pathlib import Path

from app.core.settings import Settings


def test_settings_from_file(tmp_path: Path):
    config = tmp_path / "application.yaml"
    config.write_text(
        """
neo4j:
  uri: bolt://db:7687
platform:
  api_port: 9000
        """
    )
    settings = Settings.from_file(str(config))
    assert settings.neo4j.uri == "bolt://db:7687"
    assert settings.platform.api_port == 9000
