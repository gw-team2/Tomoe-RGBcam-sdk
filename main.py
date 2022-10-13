"""
 This sample shows how to save acquired image as AVI video file.
 The following points will be demonstrated in this sample code:
 - Initialize StApi
 - Connect to camera
 - Create AVI video file
"""

import os
import tempfile
import time

import stapipy as st

# Number of images to grab
number_of_images_to_grab = 100

# Maximum number of frames in one video file
maximum_frame_count_per_file = 20

# Number of video files
video_files_count = 3


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


if __name__ == "__main__":
    try:
        # Initialize StApi before using.
        st.initialize()

        # Create a system object for device scan and connection.
        st_system: st.PyStSystem = st.create_system()

        # Connect to first detected device.
        st_device: st.PyStDevice = st_system.create_first_device()

        # Display DisplayName of the device.
        print("Device=", st_device.info.display_name)

        # Get the acquisition fps of the camera.
        fps = 50.0
        acquisition_frame_rate = st_device.remote_port.nodemap.get_node(
            "AcquisitionFrameRate"
        )
        if acquisition_frame_rate:
            fps = acquisition_frame_rate.value

        # Create PyStVideoFiler
        st_videofiler: st.PyStVideoFiler = st.create_filer(st.EStFilerType.Video)

        # Register a callback function.
        callback_info = {"error": False}
        videofiler_cb = st_videofiler.register_callback(
            videofiler_callback, callback_info
        )

        # Configure the video file settings.
        st_videofiler.maximum_frame_count_per_file = maximum_frame_count_per_file
        st_videofiler.video_file_format = st.EStVideoFileFormat.AVI2
        st_videofiler.video_file_compression = st.EStVideoFileCompression.MotionJPEG
        st_videofiler.fps = fps

        # Register video files
        filename_prefix = st_device.info.display_name
        for file_index in range(video_files_count):
            # file_location = os.path.join(tempfile.gettempdir(),
            #                          filename_prefix + str(file_index) + ".avi")
            file_location = os.path.join(filename_prefix + str(file_index) + ".avi")
            st_videofiler.register_filename(file_location)

        # Create a datastream object for handling image stream data.
        st_datastream: st.PyStDataStream = st_device.create_datastream()

        # Start the image acquisition of the host (local machine) side.
        st_datastream.start_acquisition(number_of_images_to_grab)

        # Start the image acquisition of the camera side.
        st_device.acquisition_start()

        first_frame = True
        first_timestamp = 0
        while st_datastream.is_grabbing:

            if callback_info["error"]:
                break
            with st_datastream.retrieve_buffer() as st_buffer:
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
                            st_datastream.current_fps,
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
                        tmp = delta * fps / 1000000000.0
                        frame_no = int(tmp + 0.5)

                    # Add the image data to video file.
                    st_videofiler.register_image(st_image, frame_no)
                else:
                    # If the acquired data contains no image data.
                    print("Image data does not exist.")

        # Stop the image acquisition of the camera side
        st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        st_datastream.stop_acquisition()

    except Exception as exception:
        print(exception)
