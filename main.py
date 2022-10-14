import os

from omegaconf import OmegaConf

from recorder import Recorder

if __name__ == "__main__":

    cfg = OmegaConf.load("config.yml")
    os.makedirs(cfg.video.dest_dir, exist_ok=True)
    rec = Recorder(cfg)

    while True:
        rec.grab()
