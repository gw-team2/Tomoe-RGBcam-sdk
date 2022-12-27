import tempfile


def test_record(test_config, recorder):
    with tempfile.TemporaryDirectory() as tmpd:
        test_config.video.dest_dir = tmpd
        _ = recorder.record()


def test_shot(recorder):
    _ = recorder.shot()
