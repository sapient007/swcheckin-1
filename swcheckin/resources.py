import logging

from datetime import datetime, timedelta

from flask_restful import Resource, reqparse, fields, marshal_with

from swcheckin import sched, api, db
from swcheckin.models import Reservation
from swcheckin.tasks import checkin, reminder

logger = logging.getLogger(__name__)

reservation_fields = {
    'last_name': fields.String,
    'first_name': fields.String,
    'code': fields.String,
    'flight_time': fields.DateTime,
    'uri': fields.Url('reservation')
}


class ReservationList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'code', type=str, required=True, help='No code provided')
        # we need a lambda function to handle datetime.
        # http://stackoverflow.com/questions/26662702/what-is-the-datetime-format-for-flask-restful-parser
        self.reqparse.add_argument(
            'flight_time',
            type=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'),
            required=True,
            help='Flight time should be in the format "YYYY-mm-dd HH:MM"')
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
        reservation = Reservation(
            last_name, first_name, args['code'], args['flight_time'])
        db.session.add(reservation)
        db.session.commit()
        self.schedule_checkin(reservation)
        return reservation

    def schedule_checkin(self, reservation):
        # schedule a reminder 48 hours before flight time
        sched.add_job(
            reminder,
            'date',
            run_date=reservation.flight_time - timedelta(days=2),
            args=[reservation.last_name,
                  reservation.first_name,
                  reservation.code])

        # schedule the checkin job 24 hours before the flight time
        sched.add_job(
            checkin,
            'date',
            run_date=reservation.flight_time - timedelta(days=1),
            args=[reservation.last_name,
                  reservation.first_name,
                  reservation.code])

        logger.info("Jobs scheduled: {}".format(sched.get_jobs()))


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


api.add_resource(
    ReservationList,
    '/swcheckin/api/v1/reservations/<string:last_name>/<string:first_name>',
    endpoint='reservations')
api.add_resource(
    ReservationDetail,
    '/swcheckin/api/v1/reservations/<string:last_name>/<string:first_name>/<string:code>',
    endpoint='reservation')
