import pytest
import pyogg

# Function to create an encoder and encode a sample of silence
def init_encoder(samples_per_second=48000,
                 application="audio",
                 channels=1,
                 frame_size=20, #ms
                 duration_ms=60, #ms
                 set_sampling_frequency=True,
                 set_application=True,
                 set_channels=True,
                 set_frame_size=True,
                 callback=None):
    encoder = pyogg.OpusBufferedEncoder()
    if set_application:
        encoder.set_application(application)
    if set_sampling_frequency:
        encoder.set_sampling_frequency(samples_per_second)
    if set_channels:
        encoder.set_channels(channels)
    if set_frame_size:
        encoder.set_frame_size(frame_size)

    # Create a sample of silence
    bytes_per_sample = 2
    buf = (
        b"\x00"
        * bytes_per_sample
        * channels
        * (samples_per_second // 1000)
        * duration_ms
    )

    if callback is None:
        # Encode the sample
        encoder.encode(buf)
    else:
        # Encode with callback
        encoder.encode_with_samples(buf, callback=callback)
                                    
    return encoder
    

def test_encode():
    encoder = init_encoder()


def test_callback():
    frame_size_ms = 20
    samples_per_second = 48000
    expected_samples = (
        frame_size_ms
        * samples_per_second // 1000
    )
    
    def callback(encoded_packet, samples):
        assert len(encoded_packet) > 0
        assert samples == expected_samples

    encoder = init_encoder(callback=callback)
    

def test_invalid_frame_size():
    with pytest.raises(pyogg.PyOggError):
        encoder = init_encoder(frame_size=15)
    

def test_frame_size_not_set():
    with pytest.raises(pyogg.PyOggError):
        encoder = init_encoder(set_frame_size=False)
