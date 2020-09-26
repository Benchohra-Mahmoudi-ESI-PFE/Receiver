
import argparse
import speech_recognition as sr
from os import path

parser = argparse.ArgumentParser()
parser.add_argument('--input_wav')
args = parser.parse_args()


# obtain full path to wav file
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), args.input_wav)
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
# AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  # read the entire audio file

# recognize speech using Sphinx
try:
    print("\n - Sphinx thinks you said : " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("\n - Sphinx could not understand audio")
except sr.RequestError as e:
    print("\n - Sphinx error; {0}".format(e))

# recognize keywords using Sphinx
try:
    print("\n - Sphinx recognition for \"one two three\" with different sets of keywords:")
    print(r.recognize_sphinx(audio, keyword_entries=[("one", 1.0), ("two", 1.0), ("three", 1.0)]))
except sr.UnknownValueError:
    print("\n - Sphinx could not understand audio")
except sr.RequestError as e:
    print("\n - Sphinx error; {0}".format(e))



