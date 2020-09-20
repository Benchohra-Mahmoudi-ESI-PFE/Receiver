from app import db
from sqlalchemy import func

class employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Text, primary_key=True, default=db.session.query(func.public.your_function_name()).all())
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments
