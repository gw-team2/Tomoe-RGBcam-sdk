import datetime
import os
from typing import Optional

import cv2
import numpy as np
import stapipy as st
from omegaconf import DictConfig


class Recorder:
    callback_info = {"error": False}

    @property
    def fps(self):
        return self._cfg.video.fps

    @property
    def file_dest_dir(self):
        return self._cfg.video.dest_dir

    @property
    def bufffer_size(self):
        return self._cfg.stream.buffer_size

    def __init__(self, cfg: DictConfig, filename: str) -> None:
        """
        Args:
            file_dest (str): video file path to save
            num_to_acquire (int): Number of buffers to retrieve.
        """
        self._cfg = cfg
        self._filename = filename
        path = os.path.join(self.file_dest_dir, filename)
        codec = cv2.VideoWriter_fourcc("I", "4", "2", "0")
        self._video = cv2.VideoWriter(
            path, codec, self.fps, (self._cfg.video.width, self._cfg.video.height)
        )

    def start(self, camera_index: Optional[int] = None):
        try:
            st.initialize()
            self._system: st.PyStSystem = st.create_system()

            if camera_index:
                self._camera_device: st.PyStDevice = (
                    self._system.create_device_by_index(camera_index)
                )
            else:
                self._camera_device: st.PyStDevice = self._system.create_first_device()

            self._datastream: st.PyStDataStream = (
                self._camera_device.create_datastream()
            )
            self._datastream.start_acquisition(self.bufffer_size)

            self._camera_device.acquisition_start()

            while self._datastream.is_grabbing:

                if self.callback_info["error"]:
                    break
                with self._datastream.retrieve_buffer() as st_buffer:
                    # Check if the acquired data contains image data.
                    if st_buffer.info.is_image_present:
                        # Create an image object.
                        st_image = st_buffer.get_image()
                        # Display the information of the acquired image data.
                        print(
                            "BlockID={0} Size={1} x {2} {3:.2f} fps".format(
                                st_buffer.info.frame_id,
                                st_image.width,
                                st_image.height,
                                self._datastream.current_fps,
                            )
                        )
                        data = st_image.get_image_data()
                        nparr = np.frombuffer(data, np.uint8)
                        nparr = nparr.reshape(st_image.height, st_image.width)
                        self._video.write(nparr)

                    else:
                        # If the acquired data contains no image data.
                        print("Image data does not exist.")

            self.stop()

        except Exception as exception:
            print(exception)

    def stop(self):
        self._video.release()
        self._camera_device.acquisition_stop()
        self._datastream.stop_acquisition()
