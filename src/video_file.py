from typing import Optional

import stapipy as st


class VideoFile:
    def __init__(
        self,
        fps: int,
        max_frames_per_file: int,
        file_format: st.VideoFileFormat,
        file_compression: st.VideoFileCompression,
    ) -> None:
        self._filer = st.crete_filer(st.EStFilerType.Video)
        self._fps = fps
        self._max_frames_per_file = max_frames_per_file
        self._file_format = file_format
        self._file_compression = file_compression

        self._filer.fps = self._fps
        self._filer.maximum_frame_count_per_file = self._max_frames_per_file
        self._filer.video_file_format = self._file_format
        self._filer.video_file_compression = self._file_compression

    def register_callback(self, callback, info):
        self._filer.register_callback(callback, info)

    def register_image(self, image: st.PyStImage, frame_no: int):
        self._filer.register_image(image, frame_no)
