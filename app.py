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
sys.path.insert(1, '../Speaker_Verification_Vox1/')
from hparam import hparam as hp

#sys.path.append(".")
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



@app.route('/upload_verification', methods = ['POST'])
def upload_verifiy():

    if(not request.form['AUDIO'] or not request.form['IMG']):
        return 'Données non complètes'
    
    '''print(request.form['audio-file-name'])
    print(request.form['photo-file-name'])'''


    audio_data = base64.b64decode(aes_cipher.decrypt(request.form['AUDIO']))
    audio_file_path = hp.integration.verify_upload_folder + aes_cipher.decrypt(request.form['audio-file-name'])
    img_data = base64.b64decode(aes_cipher.decrypt(request.form['IMG']))
    img_file_path = hp.integration.verify_upload_folder + aes_cipher.decrypt(request.form['photo-file-name'])
    
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)
    with open(img_file_path, 'wb') as f:
        f.write(img_data)

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
    os.system("conda run -n pytorch_main python -W ignore " + hp.integration.face_verification_path + 
    "extract_face.py --input_image " + img_file_path + 
    " --destination_dir " + hp.integration.verify_upload_folder)
    print("Time to extract face : %f" % (time.time() - start_rf1))
    
    start_rf2 = time.time()
    os.system("conda run -n vgg_py3 python -W ignore " + hp.integration.face_verification_path + 
    "identify_face.py --face_image " + os.path.splitext(img_file_path)[0]+"_visage.jpg" + " --preprocessed_dir " 
    + hp.integration.enroll_preprocessed_photo 
    + " --best_identified_faces ./")# + os.path.dirname(__file__))
    print("Time to recognize face : %f" % (time.time() - start_rf2))
    

    # + " --restriction_list " + restriction_list

    #print('\n#################### cmd2 time: '+ str(time.time() - start))

    with open('./facial_result.data', 'rb') as filehandle:
    # read the data as binary data stream
        best_identified_faces = pickle.load(filehandle)

    """ print(best_identified_speakers)
    print("") """
    print(best_identified_faces)


    print('\n######################################### Incoming Verification ... #################################################')
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
        print('\n\t'+return_msg)

    #os.system("rm " + audio_file_path + " " + img_file_path + " " + os.path.splitext(img_file_path)[0]+"_visage.jpg")
    
    print('\n\n')
    return return_msg







@app.route('/upload_enrollment', methods = [ 'POST'])
def upload_enroll():

    if( not request.form['user-firstname'] or not request.form['user-lastname'] or not request.form['AUDIO'] or not request.form['IMG']):
        return 'Données non complètes'
    
    '''print(request.form['user-firstname'] +"  "+request.form['user-lastname'])
    print(request.form['audio-file-name'])
    print(request.form['photo-file-name'])'''


    audio_data = base64.b64decode(aes_cipher.decrypt(request.form['AUDIO']))
    audio_file_path = hp.integration.enroll_upload_audio_folder + aes_cipher.decrypt(request.form['audio-file-name'])
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)
    
    img_data = base64.b64decode(aes_cipher.decrypt(request.form['IMG']))
    img_file_path = hp.integration.enroll_upload_photo_folder + aes_cipher.decrypt(request.form['photo-file-name'])
    with open(img_file_path, 'wb') as f:
        f.write(img_data)

    os.system("conda run -n voice_py3 python -W ignore "+hp.integration.speaker_verification_path+
    "verify_speaker.py --verify f --test_wav_file " + audio_file_path)
    
    os.system("conda run -n pytorch_main python " + hp.integration.face_verification_path + 
    "extract_face.py --input_image " + img_file_path + " --destination_dir "+ 
    hp.integration.enroll_preprocessed_photo)
    
    print('\n############################# Incoming Enrollment ... #################################################')
    print('\n\tSuccessfully enrolled '+ aes_cipher.decrypt(request.form['user-lastname']) + ' ' + aes_cipher.decrypt(request.form['user-firstname']))

    audio_file_path = 'uploads_enrollment/audio/' + os.path.splitext(aes_cipher.decrypt(request.form['audio-file-name']))[0] + '.npy'
    img_file_path = 'uploads_enrollment/photo/'+ os.path.splitext(aes_cipher.decrypt(request.form['photo-file-name']))[0] + '_visage.jpg'

    print('\n  Audio preprocessed and saved as : \n  ' + audio_file_path)
    print('\n  Photo preprocessed and saved as : \n  ' + img_file_path + '\n')
    
    return 'Successfully enrolled'


if __name__ == '__main__':
    #app.debug = True
    host, port = ("193.194.91.145", 5004)
    app.run(host=host, port= port, debug=True)
