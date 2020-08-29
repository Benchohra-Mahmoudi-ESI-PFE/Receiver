import os
from flask import Flask, render_template
from flask import request
import base64
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../Speaker_Verification_Vox1/')
from hparam import hparam as hp


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

    audio_data = base64.b64decode(request.form['AUDIO'])
    audio_file_path = hp.integration.verify_upload_folder + request.form['audio-file-name']
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)
    
    img_data = base64.b64decode(request.form['IMG'])
    img_file_path = hp.integration.verify_upload_folder + request.form['photo-file-name']
    with open(img_file_path, 'wb') as f:
        f.write(img_data)
    
    os.system("conda run -n voice_py3 python -W ignore "+hp.integration.speaker_verification_path+"verify_speaker.py --verify t --test_wav_file " + audio_file_path)
    
    os.system("conda run -n pytorch_main python " + hp.integration.face_verification_path + 
    "extract_face.py --input_image " + img_file_path + 
    " --destination_dir " + hp.integration.verify_upload_folder)

    os.system("conda run -n vgg_py3 python " + hp.integration.face_verification_path + 
    "identify_face.py --face_image " + os.path.splitext(img_file_path)[0]+"_visage.jpg" + " --preprocessed_dir " 
    + hp.integration.enroll_preprocessed_photo)


    return 'Envoyé avec Succès'


@app.route('/upload_enrollment', methods = [ 'POST'])
def upload_enroll():

    if( not request.form['user-firstname'] or not request.form['user-lastname'] or not request.form['AUDIO'] or not request.form['IMG']):
        return 'Données non complètes'
    
    '''print(request.form['user-firstname'] +"  "+request.form['user-lastname'])
    print(request.form['audio-file-name'])
    print(request.form['photo-file-name'])'''

    audio_data = base64.b64decode(request.form['AUDIO'])
    audio_file_path = hp.integration.enroll_upload_audio_folder + request.form['audio-file-name']
    with open(audio_file_path, 'wb') as f:
        f.write(audio_data)
    
    img_data = base64.b64decode(request.form['IMG'])
    img_file_path = hp.integration.enroll_upload_photo_folder + request.form['photo-file-name']
    with open(img_file_path, 'wb') as f:
        f.write(img_data)
    
    os.system("conda run -n voice_py3 python -W ignore "+hp.integration.speaker_verification_path+"verify_speaker.py --verify f --test_wav_file " + audio_file_path)
    
    os.system("conda run -n pytorch_main python " + hp.integration.face_verification_path + 
    "extract_face.py --input_image " + img_file_path + " --destination_dir "+ 
    hp.integration.enroll_preprocessed_photo)
    
    return 'Envoyé avec Succès'


if __name__ == '__main__':
    #app.debug = True
    host, port = ("193.194.91.145", 5004)
    app.run(host=host, port= port, debug=True)
