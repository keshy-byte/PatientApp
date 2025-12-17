from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# ---------------- Patient ----------------
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    registration_date = db.Column(db.Date, default=date.today)

    # Relationships
    vitals = db.relationship('Vitals', backref='patient', lazy=True, cascade="all, delete-orphan")
    general_assessments = db.relationship('GeneralAssessment', backref='patient', lazy=True, cascade="all, delete-orphan")
    overweight_assessments = db.relationship('OverweightAssessment', backref='patient', lazy=True, cascade="all, delete-orphan")

# ---------------- Vitals ----------------
class Vitals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)

# ---------------- General Assessment ----------------
class GeneralAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    health = db.Column(db.String(10), nullable=False)
    drugs = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.Text)

# ---------------- Overweight Assessment ----------------
class OverweightAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    health = db.Column(db.String(10), nullable=False)
    diet = db.Column(db.String(10), nullable=False)
    comments = db.Column(db.Text)
