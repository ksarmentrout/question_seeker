from question_seeker import stream as streamer


class TestStreamer:
    def test_stream(self):
        stream_result = streamer.stream('all', time_limit=1, write_to_file=False)
        assert stream_result is True
