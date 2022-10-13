import tempfile

from src.recorder import Recorder


def test_record(test_config):
    with tempfile.TemporaryDirectory() as tmpd:
        test_config.video.dest_dir = tmpd
        recorder = Recorder(test_config, "test-movie.avi")
        recorder.start()
