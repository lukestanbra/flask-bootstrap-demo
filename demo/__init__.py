import os
import click

from flask_bootstrap import Bootstrap
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)

  db_url = os.environ.get("DATABASE_URL")

  if db_url is None:
    db_path = os.path.join(app.instance_path, "demo.sqlite")
    db_url = f"sqlite:///{db_path}"
    os.makedirs(app.instance_path, exist_ok=True)

  app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY",'dev'),
    BOOTSTRAP_SERVE_LOCAL=True,
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
  )


  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.update(test_config)

  bootstrap = Bootstrap(app)
  db.init_app(app)
  csrf.init_app(app)
  app.cli.add_command(init_db_command)

  from demo import auth, blog

  app.register_blueprint(auth.bp)
  app.register_blueprint(blog.bp)
  app.add_url_rule("/", endpoint="index")

  return app

def init_db():
  db.drop_all()
  db.create_all()

@click.command("init-db")
@with_appcontext
def init_db_command():
  init_db()
  click.echo("Initialized the database")
