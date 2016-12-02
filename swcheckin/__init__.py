from pytz import utc

from flask import Flask
from flask_restful import Api

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevConfig')

api = Api(app)

db = SQLAlchemy()
db.init_app(app)

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
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc)
sched.start()
