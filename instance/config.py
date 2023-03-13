from os import environ, path
from dotenv import load_dotenv

# instance/config.py is read in after the config.py file in the directory above
# it will overwrite anything in there
basedir = path.abspath(path.dirname(__file__))
print("basedir: " + basedir)
load_dotenv(path.join(basedir, '.env'))

class Config:
    # Flask config
    FLASK_ENV = 'development'
    TESTING = True
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = environ.get('PROD_DATABASE_URI')

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')