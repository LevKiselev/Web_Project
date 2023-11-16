import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from data import db_session
from .db_session import SqlAlchemyBase
from .pictures import Picture
from .comments import Comment


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def pic_cnt(self):
        db_sess = db_session.create_session()
        res = db_sess.query(Picture).filter(self.id == Picture.user_id).count()
        db_sess.close()
        return res

    def com_cnt(self):
        db_sess = db_session.create_session()
        res = db_sess.query(Comment).filter(self.id == Comment.user_id).count()
        db_sess.close()
        return res

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now().replace(microsecond=0))
    last_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now().replace(microsecond=0))
    pictures = orm.relationship("Picture", back_populates='user')
    comments = orm.relationship("Comment", back_populates='user')
