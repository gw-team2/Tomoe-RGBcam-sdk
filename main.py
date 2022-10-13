from omegaconf import OmegaConf

from src.recorder import Recorder

if __name__ == "__main__":
    cfg = OmegaConf.load("config.yml")
    recorder = Recorder(cfg, "test-mouvie.avi")
    recorder.start()
