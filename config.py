import os

class BaseConfig(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    DEBUG = False

    # Path to our db file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    # Folder to store migration data files
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repo')


class DevConfig(BaseConfig):
    DEBUG = True
