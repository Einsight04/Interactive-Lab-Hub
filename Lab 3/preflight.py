"""Readiness check. Checks software and device capabilities without recording."""
import importlib
from exercises import ROOT


def main():
    for name in ['numpy', 'sounddevice', 'soundfile', 'sherpa_onnx', 'faster_whisper', 'piper']:
        importlib.import_module(name)
        print('OK import:', name)
    for name in ['models/silero_vad.onnx', 'voices/en_US-lessac-medium.onnx', 'voices/en_US-lessac-medium.onnx.json']:
        path = ROOT / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError('Missing model: ' + str(path))
        print('OK file:', name)
    from faster_whisper import WhisperModel
    for name in ['tiny.en', 'base.en']:
        model = WhisperModel(name, device='cpu', compute_type='int8', local_files_only=True)
        del model
        print('OK offline recognition model:', name)
    from piper import PiperVoice
    voice = PiperVoice.load(str(ROOT / 'voices/en_US-lessac-medium.onnx'))
    chunks = list(voice.synthesize('Ready.'))
    if not chunks:
        raise RuntimeError('Voice produced no samples')
    print('OK voice synthesis without playback')
    import sounddevice as sd
    print(sd.query_devices())
    sd.check_input_settings(channels=1, samplerate=16000, dtype='float32')
    sd.check_output_settings(channels=1, samplerate=chunks[0].sample_rate, dtype='int16')
    print('OK default device formats. Menu 1 must still confirm actual capture and playback.')


if __name__ == '__main__':
    main()
