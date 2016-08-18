from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64), index=True)
    first_name = db.Column(db.String(64), index=True)
    code = db.Column(db.String(10), index=True)
    flight_time = db.Column(db.DateTime)

    def __init__(self, last_name, first_name, code, flight_time):
        self.last_name = last_name
        self.first_name = first_name
        self.code = code
        self.flight_time = flight_time

    def __repr__(self):
       return '<Reservation for %r %r: %r - %r>' % (
           self.first_name, self.last_name, self.code,
           datetime.strftime(self.flight_time, '%Y-%m_%d %H:%M'))
