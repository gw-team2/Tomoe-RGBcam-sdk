import os

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import FileResponse
from omegaconf import OmegaConf

from .recorder import Recorder

CFG = "config.yml"
cfg = OmegaConf.load(CFG)
recorder = Recorder(cfg)

app = FastAPI()


@app.post("/api/record/start")
def start_record():
    pass


@app.post("/api/record/stop")
def stop_record():
    pass


@app.get("/videos")
def get_video():
    pass


@app.get("/api/shot")
async def shot():
    image: np.ndarray = recorder.shot()
    path = os.path.join("tmp", "tmp.jpg")
    cv2.imwrite(path, image)
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/config")
def set_config():
    pass
