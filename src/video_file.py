from typing import Optional

import stapipy as st


class VideoFile:
    def __init__(
        self,
        fps: int = 10,
        max_frames_per_file: int = 20,
        file_format=st.EStVideoFileFormat.AVI2,
        file_compression=st.EStVideoFileCompression.MotionJPEG,
    ) -> None:
        self._filer = st.create_filer(st.EStFilerType.Video)
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

    def register_filename(self, location: str):
        self._filer.register_filename(location)
