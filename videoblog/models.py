from . import db, session, Base
from sqlalchemy.orm import relationship
from flask_jwt_extended import  create_access_token
from datetime import timedelta
from passlib.hash import bcrypt

class Video(Base):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    @classmethod
    def get_user_list(cls, user_id):
        try:
            videos = cls.query.filter(cls.user_id == user_id).all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return videos

    @classmethod
    def get_list(cls):
        try:
            videos = cls.query.all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return videos

    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise
    @classmethod
    def get(cls, tutorial_id, user_id):
        try:
            video = cls.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
            if not video:
                raise Exception('No tutorial found')
        except Exception:
            session.rollback()
            raise
        return video


    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self,key, value)
            session.commit()
        except Exception:
            session.rollback()
            raise


    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    videos = relationship('Video', backref='user', lazy=True)


    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=24):
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email == email).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('wrong password')
        return user