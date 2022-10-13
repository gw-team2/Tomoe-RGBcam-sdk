import os

import stapipy as st
from omegaconf import DictConfig


class VideoFiler:
    def __init__(self, cfg: DictConfig, filename: str) -> None:
        self._filer = st.create_filer(st.EStFilerType.Video)
        self._cfg = cfg

        self._filer.fps = self._cfg.video.fps
        self._filer.maximum_frame_count_per_file = self._cfg.video.max_frames_per_file
        self._filer.video_file_format = eval(self._cfg.video.file_format)
        self._filer.video_file_compression = eval(self._cfg.video.file_compression)

        stem, suffix = os.path.splitext(filename)
        for file_index in range(self._cfg.video.num_video_files):
            self._filer.register_filename(
                os.path.join(self._cfg.video.dest_dir, f"{stem}_{file_index}" + suffix)
            )

    def register_callback(self, callback, info):
        self._filer.register_callback(callback, info)

    def register_image(self, image: st.PyStImage, frame_no: int):
        self._filer.register_image(image, frame_no)
