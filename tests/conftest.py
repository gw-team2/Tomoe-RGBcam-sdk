from pathlib import Path

import pytest
from omegaconf import OmegaConf


@pytest.fixture
def test_config():
    return OmegaConf.load(Path(__file__).parent / "assets" / "test_config.yml")
