from flask import Flask, render_template
from flask import request
import base64

app = Flask(__name__)

enroll_ulpoad_folder = 'uploads_enrollment/'
verifiy_upload_folder = 'uploads_verification/'


@app.route('/', methods = ['GET'])
def home():
    return render_template('home.html')#, STATE=state)

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.route('/upload_verification', methods = ['POST'])
def upload_verifiy():

    if(not request.form['user-name'] or not request.form['AUDIO'] or not request.form['IMG']):
        return 'Données non complètes'
    
    #print(request.form['user-name'])
    print(request.form['audio-file-name'])
    print(request.form['photo-file-name'])

    audio_data = base64.b64decode(request.form['AUDIO'])
    audio_file_name = verifiy_upload_folder + request.form['audio-file-name']
    with open(audio_file_name, 'wb') as f:
        f.write(audio_data)
    
    img_data = base64.b64decode(request.form['IMG'])
    img_file_name = verifiy_upload_folder + request.form['photo-file-name']
    with open(img_file_name, 'wb') as f:
        f.write(img_data)
    return 'Envoyé avec Succès'


@app.route('/upload_enrollment', methods = [ 'POST'])
def upload_enroll():

    if(not request.form['user-name'] or not request.form['AUDIO'] or not request.form['IMG']):
        return 'Données non complètes'
    
    #print(request.form['user-name'])
    print(request.form['audio-file-name'])
    print(request.form['photo-file-name'])

    audio_data = base64.b64decode(request.form['AUDIO'])
    audio_file_name = enroll_ulpoad_folder + request.form['audio-file-name']
    with open(audio_file_name, 'wb') as f:
        f.write(audio_data)
    
    img_data = base64.b64decode(request.form['IMG'])
    img_file_name = enroll_ulpoad_folder + request.form['photo-file-name']
    with open(img_file_name, 'wb') as f:
        f.write(img_data)
    return 'Envoyé avec Succès'


if __name__ == '__main__':
    #app.debug = True
    host, port = ("193.194.91.145", 5004)
    app.run(host=host, port= port, debug=True)
