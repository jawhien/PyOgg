# PyOgg

# Demo

```py
import numpy as np
import pyaudio
from damp11113 import getDBFS, RTSubtract, RTAdd
from pyogg import OpusBufferedEncoder
from pyogg import OpusDecoder
from pyogg import opus

# Initialize PyAudio
p = pyaudio.PyAudio()

# Parameters
bar = "|"
clip = "!"
bg = " "

maxrange = 10
gain = 0.01
sample_rate = 48000

# Create an Opus encoder
opus_encoder = OpusBufferedEncoder()
opus_encoder.set_application("audio")
opus_encoder.set_sampling_frequency(48000)
opus_encoder.set_channels(2)
opus_encoder.set_bitrates(19000)
#opus_encoder.set_bandwidth("narrowband")
opus_encoder.set_compresion_complex(0)
opus_encoder.set_bitrate_mode("CBR")
opus_encoder.set_frame_size(60)
#opus_encoder.set_packets_loss(100)
# Setup decoding
# ==============

# Create an Opus decoder
opus_decoder = OpusDecoder()
opus_decoder.set_channels(2)
opus_decoder.set_sampling_frequency(sample_rate)

streaminput = p.open(format=pyaudio.paInt16, channels=2, rate=sample_rate, input=True)
streamoutput = p.open(format=pyaudio.paInt16, channels=2, rate=sample_rate, output=True)

frame = 0

try:
    while True:
        try:
            pcm = np.frombuffer(streaminput.read(1024, exception_on_overflow=False), dtype=np.int16)

            if len(pcm) == 0:
                # If PCM is empty, break the loop
                break

            encoded_packets = opus_encoder.buffered_encode(memoryview(bytearray(pcm)))

            for encoded_packet, _, _ in encoded_packets:
                #print(encoded_packet, len(encoded_packet))
                decoded_pcm = opus_decoder.decode(encoded_packet)

                # Check if the decoded PCM is empty or not
                if len(decoded_pcm) > 0:
                    pcm_to_write = np.frombuffer(decoded_pcm, dtype=np.int16)

                    L = pcm_to_write[0::2]
                    R = pcm_to_write[1::2]

                    LPR = RTAdd(L, R)
                    LSR = RTSubtract(L, R)

                    IL = np.average(np.abs(L)) * 50
                    IR = np.average(np.abs(R)) * 50
                    ILB = bar * int((50 * IL / 2 ** 16) * gain)
                    IRB = bar * int((50 * IR / 2 ** 16) * gain)
                    ILB2 = ILB[:maxrange] + clip if len(ILB) > maxrange else ILB
                    IRB2 = IRB[:maxrange] + clip if len(IRB) > maxrange else IRB

                    DBFSLSR = getDBFS(LSR, 32767)
                    DBFSLPR = getDBFS(LPR, 32767)


                    if DBFSLSR > -50 and DBFSLPR > -50:
                        print(f"\r ((( ST ))) | [L {ILB2.ljust(maxrange + 1, bg)} | R {IRB2.ljust(maxrange + 1, bg)}]",
                              flush=True, end="")
                    elif DBFSLPR > -70:
                        print(f"\r    MONO    | [L {ILB2.ljust(maxrange + 1, bg)} | R {IRB2.ljust(maxrange + 1, bg)}]",
                              flush=True, end="")
                    else:
                        print(f"\r    NOIN    | [L {ILB2.ljust(maxrange + 1, bg)} | R {IRB2.ljust(maxrange + 1, bg)}]",
                              flush=True, end="")

                    streamoutput.write(pcm_to_write.tobytes())
                else:
                    print("Decoded PCM is empty")

            if frame == 100:
                opus_encoder.set_bitrate_mode("VBR")
                #print("CVBR mode")
                #opus_encoder.set_packets_loss(0)
                opus_encoder.set_compresion_complex(10)

            #print(frame)

            frame += 1

        except Exception as e:
            print(e)
            raise

except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    # Clean up PyAudio streams and terminate PyAudio
    streaminput.stop_stream()
    streaminput.close()
    streamoutput.stop_stream()
    streamoutput.close()
    p.terminate()
```

To install

```
pip install git+https://github.com/damp11113/PyOgg.git
```

PyOgg provides Python bindings for Xiph.org’s Opus, Vorbis and FLAC
audio file formats as well as their Ogg container format.

PyOgg:

- Reads and streams Opus, Vorbis, and FLAC audio formats in their
  standard file format (that is, from within Ogg containers).

- Writes Opus files (that it, Opus-formatted packets into Ogg
  containers)

- Reads and writes Opus-formatted packets (transported, for example,
  via UDP)

Further, should you wish to have still lower-level access, PyOgg
provides ctypes interfaces that give direct access to the C functions
and datatypes found in the libraries.

Under Windows, PyOgg comes bundled with the required dynamic libraries
(DLLs) in the Windows Wheel distributions.

Under macOS, the required libraries can be easily installed using
Homebrew.

PyOgg is not capable of playing audio, however, you can use Python
audio libraries such as simpleaudio, sounddevice, or PyOpenAL to play
audio. PyOpenAL even offers 3D playback.

For more detail, including installation instructions, please see the
documentation at [Read the
Docs](https://pyogg.readthedocs.io/en/latest/).
