import datetime
from typing import Optional

import stapipy as st
from omegaconf import DictConfig

from .video_file import VideoFiler


def videofiler_callback(handle=None, context=None):
    """
    Callback to handle events from Video Filer.

    :param handle: handle that trigger the callback.
    :param context: user data passed on during callback registration.
    """
    callback_type = handle.callback_type
    videofiler = handle.module
    if callback_type == st.EStCallbackType.StApiIPVideoFilerOpen:
        print("Open:", handle.data["filename"])
    elif callback_type == st.EStCallbackType.StApiIPVideoFilerClose:
        print("Close:", handle.data["filename"])
    elif callback_type == st.EStCallbackType.StApiIPVideoFilerError:
        print("Error:", handle.error[1])
        context["error"] = True


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

    def __init__(self, cfg: DictConfig) -> None:
        """
        Args:
            file_dest (str): video file path to save
            num_to_acquire (int): Number of buffers to retrieve.
        """
        self._cfg = cfg

    def start(self, camera_index: Optional[int] = None):
        try:
            st.initialize()
            self._video_filer = VideoFiler(self._cfg, "test-video.avi")
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

            first_frame = True
            first_timestamp = 0
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

                        # Calculate frame number in case of frame drop.
                        frame_no = 0
                        current_timestamp = st_buffer.info.timestamp
                        if first_frame:
                            first_frame = False
                            first_timestamp = current_timestamp
                        else:
                            delta = current_timestamp - first_timestamp
                            tmp = delta * self.fps / 1000000000.0
                            frame_no = int(tmp + 0.5)

                        # Add the image data to video file.
                        self._video_filer.register_image(st_image, frame_no)
                    else:
                        # If the acquired data contains no image data.
                        print("Image data does not exist.")

            self.stop()

        except Exception as exception:
            print(exception)

    def stop(self):
        self._camera_device.acquisition_stop()
        self._datastream.stop_acquisition()
