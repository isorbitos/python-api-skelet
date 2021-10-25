from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
import os
import logging


app = Flask(__name__)
app.config.from_object(Config)
client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager()

docs = FlaskApiSpec()


spec = APISpec(
    title="video blog",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin()]
)

app.config.update({
    'APISPEC_SPEC': spec,
    'APISPEC_SWAGGER_URL': '/swagger'
})


from .models import *

Base.metadata.create_all(bind=engine)

def setup_logger():
    logger = logging.getLogger(__name__)
    os.makedirs(os.path.dirname('log/'), exist_ok=True)
    logger.setLevel(logging.DEBUG)
    formatter =  logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return  logger

logger = setup_logger()


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

from .main.views import videos
from .users.views import users

app.register_blueprint(videos)
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)