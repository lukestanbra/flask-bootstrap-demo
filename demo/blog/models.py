from flask import url_for

from demo import db
from demo.auth.models import User


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.ForeignKey(User.id), nullable=False)
  created = db.Column(
    db.DateTime, nullable=False, server_default=db.func.current_timestamp()
  )
  title = db.Column(db.String, nullable=False)
  body = db.Column(db.String, nullable=False)

  author = db.relationship(User, lazy="joined", backref="posts")

  @property
  def update_url(self):
    return url_for("blog.update", id=self.id)

  @property
  def delete_url(self):
    return url_for("blog.delete", id=self.id)