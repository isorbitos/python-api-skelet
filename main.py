from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import VideosSchema,UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with

app = Flask(__name__)
app.config.from_object(Config)
client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()
docs.init_app(app)

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

from models import *

Base.metadata.create_all(bind=engine)



@app.get("/tutorials")
@jwt_required()
@marshal_with(VideosSchema(many=True))
def get_list():
    try:
        user_id = get_jwt_identity()
        videos = Video.query.filter(Video.user_id == user_id)
    except Exception as e:
        return {'message':str(e)}, 400
    # serialized = []
    # for video in videos:
    #     serialized.append(video.to_dict())
    # schema = VideosSchema(many=True)
    # return jsonify(schema.dump(videos))
    return videos

@app.post("/tutorials")
@jwt_required()
@use_kwargs(VideosSchema)
@marshal_with(VideosSchema)
def update_list(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_one = Video(user_id= user_id, **kwargs)
        session.add(new_one)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return new_one

@app.put("/tutorials/<int:tutorial_id>")
@jwt_required()
@use_kwargs(VideosSchema)
@marshal_with(VideosSchema)
def update_tutorial(tutorial_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
        if not item:
            return {'message':'No tutorial fount with this id'}, 400
        for key, value in kwargs.items():
            setattr(item, key, value)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return item

@app.delete("/tutorials/<int:tutorial_id>")
@jwt_required()
@marshal_with(VideosSchema)
def delete_tutorial(tutorial_id):
    try:
        user_id = get_jwt_identity()
        item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
        if not item:
            return {'message': 'No tutorial fount with this id'}, 400
        session.delete(item)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return {'message':'Item deleted'}, 204

@app.post('/register')
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    try:
        user = User(**kwargs)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {'access_token': token}

@app.post('/login')
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def login(**kwargs):
    try:
        user = User.authenticate(**kwargs)
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {'access_token': token}

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

@app.errorhandler(422)
def error_handler(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request'])
    if headers:
        return jsonify({'message':messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400

docs.register(get_list)
docs.register(update_list)
docs.register(update_tutorial)
docs.register(delete_tutorial)
docs.register(register)
# docs.register(login)