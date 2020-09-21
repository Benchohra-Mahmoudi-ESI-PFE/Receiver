from app import db
from sqlalchemy import func



class employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Text, primary_key=True, default=db.session.query(func.public.generate_uid(5)).all())
    employee_first_name = db.Column(db.String(50))
    employee_last_name = db.Column(db.String(50))
    employee_phone = db.Column(db.String(12),  unique=True)
    employee_proffession = db.Column(db.String(50))
    employee_banned = db.Column(db.Date, default='') # '' <==> not banned | not empty value <==> banned
    employee_role = db.Column(db.String(200))
    

    def __init__(self, first_name, last_name, phone, proffession, banned, role):
        self.employee_first_name = first_name
        self.employee_last_name = last_name
        self.employee_phone = phone
        self.employee_proffession = proffession
        self.employee_banned = banned  # '' <==> not banned | not empty value <==> banned
        self.employee_role = role

class rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Text, primary_key=True, default=db.session.query(func.public.generate_uid(5)).all())
    num_block = db.Column(db.Integer)
    num_floor = db.Column(db.Integer)
    num_door = db.Column(db.Integer)
    room_description = db.Column(db.String(200))

    def __init__(self, num_block, num_floor, num_door, room_description):
        self.num_block = num_block
        self.num_floor = num_floor
        self.num_door = num_door
        self.room_description = room_description

class has_access(db.Model):
    __tablename__ = 'has_access'
    employee_id = db.Column(db.Text, db.ForeignKey(employees.id), primary_key=True)
    room_id = db.Column(db.Text, db.ForeignKey(rooms.id), primary_key=True)
    date_has_access = db.Column(db.Date)
    time_has_access = db.Column(db.Time)
    description_has_access = db.Column(db.String(200))

    employee = db.relationship('employees', foreign_keys='has_access.employee_id')
    room = db.relationship('rooms', foreign_keys='has_access.room_id')
    
    def __init__(self, employee_id, room_id, date_has_access, time_has_access):
        self.employee_id = employee_id
        self.room_id = room_id
        self.date_has_access = date_has_access
        self.time_has_access = time_has_access
    
class log_inscription(db.Model):
    __tablename__ = 'log_inscription'
    id = db.Column(db.Text, primary_key=True, default=db.session.query(func.public.generate_uid(5)).all())
    facial_biometric = db.Column(db.Text, unique=True)
    vocal_biometric = db.Column(db.Text, unique=True)
    employee_id = db.Column(db.Text, db.ForeignKey(employees.id))
    date_inscription = db.Column(db.Date)
    time_inscription = db.Column(db.Time)
    inscription_description = db.Column(db.String(200))

    employee = db.relationship('employees', foreign_keys='log_inscription.employee_id')

    def __init__(self, facial_biometric, vocal_biometric, employee_id, date_inscription, time_inscription, inscription_description):
        self.facial_biometric = facial_biometric
        self.vocal_biometric = vocal_biometric
        self.employee_id = employee_id
        self.date_inscription = date_inscription
        self.time_inscription = time_inscription
        self.inscription_description = inscription_description


class log_verification(db.Model):
    __tablename__ = 'log_verification'
    employee_id = db.Column(db.Text, db.ForeignKey(employees.id), primary_key=True)
    room_id = db.Column(db.Text, db.ForeignKey(rooms.id), primary_key=True)
    date_verification = db.Column(db.Date, primary_key=True)
    time_verification = db.Column(db.Time, primary_key=True)
    verification_description = db.Column(db.String(200))

    employee = db.relationship('employees', foreign_keys='log_verification.employee_id')
    room = db.relationship('rooms', foreign_keys='log_verification.room_id')

    def __init__(self, employee_id, room_id, date_verification, time_verification, verification_description):
        self.employee_id = employee_id
        self.room_id = room_id
        self.date_verification = date_verification
        self.time_verification = time_verification
        self.verification_description = verification_description


'''
'''

# audio_file_path = 'uploads_enrollment/audio/' + os.path.splitext(aes_cipher.decrypt(request.form['audio-file-name']))[0] + '.npy'
# img_file_path = 'uploads_enrollment/photo/'+ os.path.splitext(aes_cipher.decrypt(request.form['photo-file-name']))[0] + '_visage.jpg'
