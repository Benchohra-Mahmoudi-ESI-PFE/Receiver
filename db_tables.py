from app import db
from sqlalchemy import func



class employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Text, primary_key=True, default=db.session.query(func.public.generate_uid(5)).all())
    employee_first_name = db.Column(db.String(200))
    employee_last_name = db.Column(db.String(200))
    employee_phone = db.Column(db.String(200))
    employee_last_name = db.Column(db.String(200))
    
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

'''
if hp.app.ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + 
    hp.app.dev_db_username + ':' +
    hp.app.dev_db_password + '@' +
    hp.app.dev_db_host + '/' +
    hp.app.dev_db_name
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

'''

# audio_file_path = 'uploads_enrollment/audio/' + os.path.splitext(aes_cipher.decrypt(request.form['audio-file-name']))[0] + '.npy'
# img_file_path = 'uploads_enrollment/photo/'+ os.path.splitext(aes_cipher.decrypt(request.form['photo-file-name']))[0] + '_visage.jpg'
