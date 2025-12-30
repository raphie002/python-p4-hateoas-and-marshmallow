# server/models.py
from flask_sqlalchemy import SQLAlchemy # type: ignore

db = SQLAlchemy()

class Newsletter(db.Model):
    __tablename__ = 'newsletters'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    published_at = db.Column(db.DateTime, server_default=db.func.now())
    edited_at = db.Column(db.DateTime, onupdate=db.func.now())

    comments = db.relationship('Comment', backref='newsletter', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Newsletter {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    newsletter_id = db.Column(db.Integer, db.ForeignKey('newsletters.id'))

    def __repr__(self):
        return f'<Comment {self.text[:20]}...>'