#!/usr/bin/env python
from pytz import utc
from datetime import datetime

from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal_with

from app.models import db, Reservation
from app.tasks import checkin
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


app = Flask(__name__)
app.config.from_object('config.DevConfig')
db.init_app(app)
api = Api(app)


reservation_fields = {
    'last_name': fields.String,
    'first_name': fields.String,
    'code': fields.String,
    'flight_time': fields.DateTime,
    'uri': fields.Url('reservation')
}

# configurations for the scheduler
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

sched = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
sched.start()


class ReservationList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'code', type=str, required=True, help='No code provided')
        # we need a lambda function to handle datetime.
        # http://stackoverflow.com/questions/26662702/what-is-the-datetime-format-for-flask-restful-parser
        self.reqparse.add_argument(
            'flight_time', type=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'),
            required=True, help='Flight time should be in the format "YYYY-mm-dd HH:MM"')
        super(ReservationList, self).__init__()

    @marshal_with(reservation_fields)
    def get(self, first_name, last_name):
        reservations = Reservation.query.filter_by(
            last_name=last_name, first_name=first_name).all()
        # TODO: Add message if no reservations found
        return reservations

    @marshal_with(reservation_fields)
    def post(self, last_name, first_name):
        args = self.reqparse.parse_args()
        reservation = Reservation(last_name, first_name, args['code'], args['flight_time'])
        db.session.add(reservation)
        db.session.commit()
        self.schedule_checkin(reservation)
        return reservation

    def schedule_checkin(self, reservation):
        job = sched.add_job(
            checkin, 'date', run_date=reservation.flight_time, args=[
                reservation.last_name, reservation.first_name, reservation.code])
        print(sched.get_jobs())


class ReservationDetail(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('code', type=str, location='json')
        super(ReservationDetail, self).__init__()

    @marshal_with(reservation_fields)
    def get(self, last_name, first_name, code):
        # TODO: prevent dupes from getting created
        reservation = Reservation.query.filter_by(
            last_name=last_name, first_name=first_name, code=code).first()
        return reservation


api.add_resource(ReservationList,
                 '/swcheckin/api/v1/reservations/<string:last_name>/<string:first_name>',
                 endpoint='reservations')
api.add_resource(ReservationDetail,
                 '/swcheckin/api/v1/reservations/<string:last_name>/<string:first_name>/<string:code>',
                 endpoint='reservation')


if __name__ == "__main__":
    app.run(debug=True)
