"""
 This sample shows how to use StApi with OpenCV for format conversion and display.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Acquire image data
 - Copy image data for OpenCV
 - Convert Bayer image format to RGB using OpenCV
 - Preview image using OpenCV
 Note: opencv-python and numpy packages are required:
    pip install numpy
    pip install opencv-python
"""

import os
from datetime import datetime
from typing import Union

import cv2
import numpy as np
import stapipy as st
from omegaconf import DictConfig


class Recorder:
    @property
    def fps(self):
        return self._cfg.video.fps

    @property
    def video_seconds(self):
        return self._cfg.video.seconds

    @property
    def frame_width(self):
        return self._cfg.video.width

    @property
    def frame_height(self):
        return self._cfg.video.height

    @property
    def num_grabs(self):
        return self.fps * self.video_seconds

    def __init__(self, cfg: DictConfig) -> None:
        self._cfg = cfg
        st.initialize()
        self._system = st.create_system()

        self._device = self._system.create_first_device()
        print("Device=", self._device.info.display_name)
        self._device.remote_port.nodemap.get_node(
            "AcquisitionFrameRate"
        ).value = self.fps

        self._datastream = self._device.create_datastream()

    def _get_video_path(self):
        dest_dir = self._cfg.video.dest_dir
        timestamp = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        return os.path.join(dest_dir, timestamp + ".avi")

    def _preprocess_record(self, num_grabs: int):
        self._datastream.start_acquisition(num_grabs)
        self._device.acquisition_start()

    def _postprocess_record(self):
        self._device.acquisition_stop()
        self._datastream.stop_acquisition()

    def record(self) -> str:
        """
        Record video and save video file.
        Returns:
            File path of recorded video.
        """
        try:
            video_path = self._get_video_path()
            codec = cv2.VideoWriter_fourcc("I", "4", "2", "0")
            self._writer = cv2.VideoWriter(
                video_path, codec, self.fps, (self.frame_width, self.frame_height)
            )

            self._preprocess_record(self.num_grabs)

            while self._datastream.is_grabbing:
                with self._datastream.retrieve_buffer() as st_buffer:
                    if st_buffer.info.is_image_present:
                        cap_img = st_buffer.get_image()

                        print(
                            "BlockID={0} Size={1} x {2} First Byte={3}".format(
                                st_buffer.info.frame_id,
                                cap_img.width,
                                cap_img.height,
                                cap_img.get_image_data()[0],
                            )
                        )
                        nparr = self._convert(cap_img)
                        self._writer.write(nparr)
                    else:
                        print("Image data does not exist.")

        except Exception as exception:
            print(exception)

        finally:
            self.stop()
            return video_path

    def shot(self) -> Union[np.ndarray, None]:
        """
        Capture image.
        Returns:
            image: np.ndarray. if failed to capture a image, this function returns null.
        """

        try:
            self._preprocess_record(1)
            with self._datastream.retrieve_buffer() as st_buffer:
                if st_buffer.info.is_image_present:
                    cap_img = st_buffer.get_image()
                    nparr = self._convert(cap_img)
                else:
                    nparr = None

        except Exception as exception:
            print(exception)

        finally:
            self._postprocess_record()
            return nparr

    def stop(self):
        self._writer.release()
        cv2.destroyAllWindows()

        self._postprocess_record()

    def _convert(self, cap_img):
        # Check the pixelformat of the input image.
        pixel_format = cap_img.pixel_format
        pixel_format_info = st.get_pixel_format_info(pixel_format)

        # Only mono or bayer is processed.
        if not (pixel_format_info.is_mono or pixel_format_info.is_bayer):
            return

        # Get raw image data.
        data = cap_img.get_image_data()

        # Perform pixel value scaling if each pixel component is
        # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
        if pixel_format_info.each_component_total_bit_count > 8:
            nparr = np.frombuffer(data, np.uint16)
            division = pow(2, pixel_format_info.each_component_valid_bit_count - 8)
            nparr = (nparr / division).astype("uint8")
        else:
            nparr = np.frombuffer(data, np.uint8)

        # Process image for display.
        nparr = nparr.reshape(cap_img.height, cap_img.width, 1)

        # Perform color conversion for Bayer.
        if pixel_format_info.is_bayer:
            bayer_type = pixel_format_info.get_pixel_color_filter()
            if bayer_type == st.EStPixelColorFilter.BayerRG:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
            elif bayer_type == st.EStPixelColorFilter.BayerGR:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
            elif bayer_type == st.EStPixelColorFilter.BayerGB:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
            elif bayer_type == st.EStPixelColorFilter.BayerBG:
                nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)
        else:
            nparr = nparr[:, :, ::-1]  # BGR -> RGB
        return nparr
