from pathlib import Path

import pytest
from omegaconf import OmegaConf

from src.recorder import Recorder


@pytest.fixture
def test_config():
    return OmegaConf.load(Path(__file__).parent / "assets" / "test_config.yml")


@pytest.fixture
def recorder(test_config):
    return Recorder(test_config)
