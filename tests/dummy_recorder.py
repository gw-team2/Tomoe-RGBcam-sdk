from omegaconf import DictConfig

from src.recorder import Recorder


class DummyRecorder(Recorder):
    def __init__(self, cfg: DictConfig):
        self._cfg = cfg

    def _preprocess_record(self, num_grabs: int):
        pass

    def _postprocess_record(self):
        pass

    def record(self):
        pass

    def shot(self):
        pass
