import datetime
import sqlalchemy
from sqlalchemy import orm
from data import db_session
from .comments import Comment
from .db_session import SqlAlchemyBase


class Picture(SqlAlchemyBase):
    __tablename__ = 'pictures'

    def com_cnt(self):
        db_sess = db_session.create_session()
        return db_sess.query(Comment).filter(self.id == Comment.picture_id).count()

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    descr = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now().replace(microsecond=0))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    comments = orm.relationship("Comment", back_populates='picture')
