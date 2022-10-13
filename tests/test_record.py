from omegaconf import OmegaConf
from src.recorder import Recorder


def test_record(test_config):
    recorder = Recorder(test_config)
