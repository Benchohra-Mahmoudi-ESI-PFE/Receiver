# -*- coding: UTF-8 -*-

import os
from flask import Flask, render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import numpy
import base64
import time
import pickle
import subprocess

import sys
sys.path.insert(1, '../config')
from hparam import hparam as hp

from aes_utils import AESCipher

key = 'this is my key'
aes_cipher = AESCipher(key)

# Initiating the Flask app
app = Flask(__name__)


@app.route('/', methods = ['GET'])
def home():
    return render_template('home.html')#, STATE=state)

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################


@app.route('/upload_verification', methods = ['POST'])
def upload_verify():

    print('\n\n\n\n ########################### Incoming Verification ... ########################### \n')

    if not request.form['IMG'] \
    or not request.form['AUDIO'] \
    or not request.form['timestamp']:
        return 'Données non complètes'
        

    # Decrpting data
    img_data_encoded = aes_cipher.decrypt(request.form['IMG'])
    audio_data_encoded = aes_cipher.decrypt(request.form['AUDIO'])
    timestamp = aes_cipher.decrypt(request.form['timestamp'])

    # Decoding image and audio data
    img_data = base64.b64decode(img_data_encoded)
    audio_data = base64.b64decode(audio_data_encoded)

    # Writing image data to disk
    img_file_name = timestamp + "_verify_photo.jpg"
    img_file_path = hp.integration.verify_upload_folder + img_file_name
    with open(img_file_path, 'wb') as f:
        f.write(img_data)
    
    # Writing audio data to disk
    audio_file_name = timestamp + "_verify_audio.m4a"
    audio_file_path = hp.integration.verify_upload_folder + audio_file_name
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)


    # -----------------------------------
    print('\n    Verifying the voice...')
    # -----------------------------------

    start_rv = time.time()
    err_code_rv = os.system("conda run -n voice_py3 python " 
                                + hp.integration.speaker_verification_path + "verify_speaker.py" 
                                + " --verify t " 
                                + " --test_wav_file " + audio_file_path
                                + " --best_identified_speakers ./")
    print("\t Time to recognize voice : %f" % (time.time() - start_rv))

    if (err_code_rv == 0):
        # Clean execution of voice extraction module
        pass
        
    with open('./speaker_result.data', 'rb') as filehandle:
        best_identified_speakers = pickle.load(filehandle)

    id = best_identified_speakers[0][0]
    score = best_identified_speakers[0][1]
    lname = id.split('_')[2]
    fname = id.split('_')[3]
    print('\n\t Identified as : %s %s - (precision : %d%%)' % (lname, fname, int(100*score)))
    
    # restriction_list = [x[0] for x in best_identified_speakers]
    # print(restriction_list)


    # -----------------------------------
    print('\n     Verifying the face...')
    # -----------------------------------

    start_rf1 = time.time()
    err_code_rf1 = os.system("conda run -n pytorch_main python " 
                                + hp.integration.face_verification_path + "extract_face.py" 
                                + " --input_image " + img_file_path 
                                + " --destination_dir " + hp.integration.verify_upload_folder)
    print("\t Time to extract face : %f" % (time.time() - start_rf1))

    
    start_rf2 = time.time()
    err_code_rf2 = os.system("conda run -n vgg_py3 python -W ignore " 
                                + hp.integration.face_verification_path + "identify_face.py" 
                                + " --face_image " + img_file_path.replace(".jpg", "_visage.jpg") 
                                + " --preprocessed_dir " + hp.integration.enroll_preprocessed_photo 
                                + " --best_identified_faces ./")
    print("\t Time to recognize face : %f" % (time.time() - start_rf2))

    if (err_code_rf1 + err_code_rf2 == 0):
        #Clean execution of face extraction and face identification modules
        pass
    
    with open('./facial_result.data', 'rb') as filehandle:
        best_identified_faces = pickle.load(filehandle)

    id = best_identified_faces[0][0]
    score = best_identified_faces[0][1]
    lname = id.split('_')[2]
    fname = id.split('_')[3]
    print('\n\t Identified as : %s %s - (precision : %d%%)' % (lname, fname, int(100*score)))
    
    # -----------------------------------
    # -----------------------------------

    if (best_identified_faces[0][1] > hp.integration.face_threshold): # and (best_identified_speakers[0][0] == best_identified_faces[0][0]):
        # Delete user data since succeessfully identified
        os.system("rm " + "./speaker_result.data " + " " + audio_file_path)
        os.system("rm " + "./facial_result.data" + " " + img_file_path + " " + img_file_path.replace(".jpg", "_visage.jpg"))
        return_msg = 'Bienvenue, ' + ' '.join(best_identified_faces[0][0].split('_')[2:4])
        print('\n\t Identity confirmed successfully, ' + lname + ' ' + fname)
    elif (best_identified_speakers[0][0] != best_identified_faces[0][0]):
        return_msg = 'Partiellement reconnu, réessayez'
        print('\n\t Face and voice mismatch, waiting for retry...')
    else:
        return_msg = 'Non reconnu'
        print('\n\t' + 'Not recognized')

    print("\n Ordered list of speakers :")
    print(best_identified_speakers)
    print("\n Ordered list of faces :")
    print(best_identified_faces)


    print('\n\n')
    return return_msg



##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################



@app.route('/upload_enrollment', methods = [ 'POST'])
def upload_enroll():
    
    print('\n\n\n\n ########################### Incoming Enrollment ... ########################### \n')

    if not request.form['IMG'] \
    or not request.form['AUDIO'] \
    or not request.form['user-firstname'] \
    or not request.form['user-lastname'] \
    or not request.form['timestamp']:
        return 'Données non complètes'


    # Decrypting data
    img_data_encoded = aes_cipher.decrypt(request.form['IMG'])
    audio_data_encoded = aes_cipher.decrypt(request.form['AUDIO'])
    fname = aes_cipher.decrypt(request.form['user-firstname'])
    lname = aes_cipher.decrypt(request.form['user-lastname'])
    timestamp = aes_cipher.decrypt(request.form['timestamp'])

    # Decoding image and audio data
    img_data = base64.b64decode(img_data_encoded)
    audio_data = base64.b64decode(audio_data_encoded)

    user_id = timestamp + "_" + lname + "_" + fname

    # Writing image data to disk
    img_file_name = user_id + "_enroll_photo.jpg"
    img_file_path = hp.integration.enroll_upload_photo_folder + img_file_name
    with open(img_file_path, 'wb') as f:
        f.write(img_data)
    
    # Writing audio data to disk
    audio_file_name = user_id + "_enroll_audio.m4a"
    audio_file_path = hp.integration.enroll_upload_audio_folder + audio_file_name
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)

    start_rv = time.time()
    err_code_rv = os.system("conda run -n voice_py3 python -W ignore " 
                                + hp.integration.speaker_verification_path + "verify_speaker.py" 
                                + " --verify f " 
                                + " --test_wav_file " + audio_file_path)
    print("Time to extract voice embeddings : %f" % (time.time() - start_rv))

    start_rf1 = time.time()
    err_code_rf1 = os.system("conda run -n pytorch_main python -W ignore " 
                                + hp.integration.face_verification_path + "extract_face.py" 
                                + " --input_image " + img_file_path 
                                + " --destination_dir " + hp.integration.enroll_upload_photo_folder)
    print("Time to extract face : %f" % (time.time() - start_rf1))

    start_rf1_1 = time.time()
    input_face_image = hp.integration.enroll_upload_photo_folder + img_file_name.replace(".jpg", "_visage.jpg")
    err_code_rf2 = os.system("conda run -n vgg_py3 python -W ignore " 
                                + hp.integration.face_verification_path + "save_face_embeddings.py"
                                + " --input_image " + input_face_image
                                + " --destination_dir " + hp.integration.enroll_preprocessed_photo)
    print("Time to get and save embeddings : %f" % (time.time() - start_rf1_1))

    # if (err_code_rf1 + err_code_rf2 == 0):
    #     os.system("rm " + img_file_path + " " + input_face_image)


    print('\n Successfully enrolled ' + lname + ' ' + fname)

    print('\n Photo and audio preprocessed and saved under the ID : ' + user_id + '\n')
    
    return 'Inscription réussie'


if __name__ == '__main__':
    #app.debug = True
    host, port = ("193.194.91.145", 5004)
    app.run(host=host, port= port, debug=True)
