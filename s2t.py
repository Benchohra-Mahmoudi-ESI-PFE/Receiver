import time
start = time.time()

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input_m4a')
args = parser.parse_args()

def word_to_num(s):
    numbers  = {'zero':'0',
                'one':'1',
                'two':'2',
                'three':'3',
                'four':'4',
                'five':'5',
                'six':'6',
                'seven':'7',
                'eight':'8',
                'nine':'9'}
    return numbers.get(s,"Not an integer")

def words_to_digits(words_list):
    digits = ""
    for word in words_list:
        digits += word_to_num(word)
    if "Not an integer" in digits:
        return "One or more of the inputs is not an integer"
    return digits
    

os.system("ffmpeg -loglevel quiet -i " + args.input_m4a + " audio_file.wav")
os.system("deepspeech" 
        + " --model deepspeech_model.pbmm " 
        + " --scorer deepspeech_model.scorer " 
        + " --audio  audio_file.wav "
        + "  > speech-to-text_result 2>&1")

with open("speech-to-text_result", 'rt') as f:
    lines = f.readlines()

os.system("rm speech-to-text_result")
# os.system("rm converting_output")
os.system("rm audio_file.wav")

inference_time = lines[-2].replace("Inference", "Speech text recognition").replace("\n", "")
speech_full = lines[-1]
door_number_words = speech_full.replace("\n", "").split(" ")[-4:]

print(" - Speech text recognition took : %s" % inference_time)
print(" - Door number (words) : %s" % str(door_number_words))
print(" - Door number (digits) : %s" % words_to_digits(door_number_words))


print("\n\t - Total execution time : %s \n" % (time.time() - start))

