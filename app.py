# -*- coding: UTF-8 -*-

import os
from flask import Flask, render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import numpy
import base64
import time
import pickle
import sys
import subprocess

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../config/')
from hparam import hparam as hp

#sys.path.append(".")
from aes_utils import AESCipher

key = 'this is my key'
aes_cipher = AESCipher(key)

# Initiating the Flask app
app = Flask(__name__)

# Configuring the database connection
if hp.app.ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + \
    hp.app.dev_db_username + ':' + \
    hp.app.dev_db_password + '@' + \
    hp.app.dev_db_host +  ':5432' +'/' + \
    hp.app.dev_db_name
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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

    print('\n######################################### Incoming Verification ... #################################################')

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
        

    start_rv = time.time()
    # print(start_rv)

    # _ = subprocess.run(["conda run -n voice_py3 python -W ignore " + hp.integration.speaker_verification_path
    #              + "verify_speaker.py --verify t --test_wav_file " + audio_file_path
    #              + " --best_identified_speakers ./"]
    #          , check=True)
    # print("after %f" % (time.time - start_rv))

    ## commented while the error is fixed

    """ os.system("conda run -n voice_py3 python -W ignore " + hp.integration.speaker_verification_path
    + "verify_speaker.py --verify t --test_wav_file " + audio_file_path + 
    " --best_identified_speakers ./")

    with open('./speaker_result.data', 'rb') as filehandle:
    # read the data as binary data stream
        best_identified_speakers = pickle.load(filehandle)

    print("Time to recognize voice : %f" % (time.time() - start_rv)) """

    #restriction_list = [x[0] for x in best_identified_speakers]
    #print(restriction_list)
    #time.sleep(5)



    start_rf1 = time.time()
    err_code_rf1 = os.system("conda run -n pytorch_main python " 
                                + hp.integration.face_verification_path + "extract_face.py" 
                                + " --input_image " + img_file_path 
                                + " --destination_dir " + hp.integration.verify_upload_folder)
    print("Time to extract face : %f" % (time.time() - start_rf1))

    
    start_rf2 = time.time()
    err_code_rf2 = os.system("conda run -n vgg_py3 python -W ignore " 
                                + hp.integration.face_verification_path + "identify_face.py" 
                                + " --face_image " + img_file_path.replace(".jpg", "_visage.jpg") 
                                + " --preprocessed_dir " + hp.integration.enroll_preprocessed_photo 
                                + " --best_identified_faces ./")
    print("Time to recognize face : %f" % (time.time() - start_rf2))

    # read the data as binary data stream
    with open('./facial_result.data', 'rb') as filehandle:
        best_identified_faces = pickle.load(filehandle)
    
    # Delete user data if succeessfully identified
    if (err_code_rf1 + err_code_rf2 == 0):
        os.system("rm " + "./facial_result.data" + " " + img_file_path + " " + img_file_path.replace(".jpg", "_visage.jpg"))


    """ print(best_identified_speakers)
    print("") """
    print(best_identified_faces)


    """ print('\n\tVerifying the speech...')
    id = best_identified_speakers[0][0]
    lname = id.split('_')[2]
    fname = id.split('_')[3]
    score = best_identified_speakers[0][1]
    print('\tIdentified as : %s %s - (precision : %d%%)' % (lname, fname, int(100*score)))
    #print('\n\t\tIdentified as :  '+ str(best_identified_speakers[0]))# a[0] + ' ' + str(a[1]) for a in best_identified_speakers)
 """    
    print('\n\tVerifying the face...')
    #print('\n\t\tFace :  '+ str(best_identified_faces[0]))#a[0] + ' ' + str(a[1]) for a in best_identified_faces)
    id = best_identified_faces[0][0]
    lname = id.split('_')[2]
    fname = id.split('_')[3]
    score = best_identified_faces[0][1]
    print('\tIdentified as : %s %s - (precision : %d%%)' % (lname, fname, int(100*score)))

    if (best_identified_faces[0][1] > hp.integration.face_threshold): # and (best_identified_speakers[0][0] == best_identified_faces[0][0]):
        return_msg = 'Welcome ' + ' '.join(best_identified_faces[0][0].split('_')[2:4])
        print('\n\tIdentity confirmed successfully, ' + lname + ' ' + fname)
        #print('\n ' + ' '.join(best_identified_faces[0][0].split('_')[2:4]) + '  ' + str(best_identified_faces[0][1]) + ' ' + str(best_identified_speakers[0][1]))
    elif (best_identified_speakers[0][0] != best_identified_faces[0][0]):
        return_msg = 'Face and voice mismatch, try again'
        print('\n\tFace and voice mismatch, waiting for retry...')
        #print('\n ' + ' '.join(best_identified_faces[0][0].split('_')[2:4]) + '  ' + str(best_identified_faces[0][1]) + ' ' + str(best_identified_speakers[0][1]))

    else:
        return_msg = 'Not recognized'
        print('\n\t' + return_msg)


    print('\n\n')
    return return_msg


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################



@app.route('/upload_enrollment', methods = [ 'POST'])
def upload_enroll():
    
    print('\n############################# Incoming Enrollment ... #################################################')

    if not request.form['IMG'] \
    or not request.form['AUDIO'] \
    or not request.form['user-firstname'] \
    or not request.form['user-lastname'] \
    or not request.form['timestamp']:
        return 'Données non complètes'


    # Decrpting data
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
    
    return 'Successfully enrolled'


if __name__ == '__main__':
    #app.debug = True
    host, port = ("193.194.91.145", 5004)
    app.run(host=host, port= port, debug=True)
