from omegaconf import OmegaConf

from recorder import Recorder

if __name__ == "__main__":
    cfg = OmegaConf.load("config.yml")
    rec = Recorder(cfg)

    while True:
        rec.grab()
