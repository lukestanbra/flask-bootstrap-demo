from datetime import datetime
import os
import pytest
from werkzeug.security import generate_password_hash

from demo import create_app
from demo import db
from demo import init_db
from demo.auth.models import User
from demo.blog.models import Post
from flask import g, url_for

_user1_pass = generate_password_hash("test")
_user2_pass = generate_password_hash("other")


@pytest.fixture
def app():
  """Create and configure a new app instance for each test."""
  # create the app with common test config
  app = create_app({
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "WTF_CSRF_ENABLED": False
    })

  # create the database and load test data
  # set _password to pre-generated hashes, since hashing for each test is slow
  with app.app_context():
    init_db()
    user = User(username="test", _password=_user1_pass)
    db.session.add_all(
      (
        user,
        User(username="other", _password=_user2_pass),
        Post(
          title="test title",
          body="test\nbody",
          author=user,
          created=datetime(2018, 1, 1),
        ),
      )
    )
    db.session.commit()

  yield app

# This is needed for retrieving the csrf token from g
# So that the requests don't fail the form.validate_on_submit() check
@pytest.fixture
def app_cxt(app):
  with app.app_context() as ctx:
    yield ctx

@pytest.fixture
def client(app):
  """A test client for the app."""
  return app.test_client()


@pytest.fixture
def runner(app):
  """A test runner for the app's Click commands."""
  return app.test_cli_runner()


class AuthActions:
  def __init__(self, client, app_cxt):
    self._client = client
    self._app_cxt = app_cxt

  def login(self, username="test", password="test"):
    with self._app_cxt:
      self._client.get(url_for("auth.login"))
      return self._client.post(
        url_for("auth.login"), data={"username": username, "password": password, "csrf_token": g.get('csrf_token')},
        follow_redirects=True
      )

  def logout(self):
    return self._client.get(url_for("auth.logout"))


@pytest.fixture
def auth(client, app_cxt):
  return AuthActions(client, app_cxt)

# Allows the use of url_for in tests
@pytest.fixture(autouse=True)
def _push_request_context(request, app):
  ctx = app.test_request_context()  # create context
  ctx.push()  # push

  def teardown():
      ctx.pop()  # pop

  request.addfinalizer(teardown)  # set teardown