"""from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    noise_db = db.Column(db.Float, nullable=False)
"""
from app import db

class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    decibel = db.Column(db.Float)
    hertz = db.Column(db.Float)
    source = db.Column(db.String(50))
