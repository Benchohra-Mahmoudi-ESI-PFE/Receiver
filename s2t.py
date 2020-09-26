import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input_wav')
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
    

os.system("deepspeech" 
        + " --model deepspeech_model.pbmm " 
        + " --scorer deepspeech_model.scorer " 
        + " --audio " + args.input_wav 
        + "  > speech-to-text_result 2>&1")

with open("speech-to-text_result", 'rt') as f:
    lines = f.readlines()
os.system("rm speech-to-text_result")

time = lines[-2].replace("Inference", "Speech text recognition")
speech_full = lines[-1]
door_number_words = speech_full.replace("\n", "").split(" ")[-4:]

print("\n - Speech text recognition took : " + time)
print("\n - Door number (words) : " + str(door_number_words))
print("\n - Door number (digits) : " + words_to_digits(door_number_words))

