import pytest
from flask import g, session, url_for
from demo.auth.models import User

#  print(response.get_data(as_text=True))

def test_register(client, app, app_cxt):
  assert client.get(url_for("auth.register")).status_code == 200

  response = client.post(
    url_for("auth.register"),
    data={"username": "abc", "password": "abc", "csrf_token": g.get('csrf_token')}
  )
  assert f"http://localhost{url_for('auth.login')}" == response.location

def test_user_password(app):
  user = User(username="abc", password="abc")
  assert user.password != "abc"
  assert user.check_password("abc")

@pytest.mark.parametrize(
  ("username", "password", "message"),
  (
    ("", "", b"This field is required."),
    ("a", "", b"This field is required."),
    ("test", "test", b"already registered"),
  ),
)
def test_register_validate_input(client, app_cxt, username, password, message):
  assert client.get(url_for("auth.register")).status_code == 200
  response = client.post(
    url_for("auth.register"), data={"username": username, "password": password, "csrf_token": g.get('csrf_token')}
  )
  assert message in response.data

def test_login(client, auth):
  with client:
    response = auth.login()
    assert response.history[0].location in f"http://localhost{url_for('blog.index')}"
    assert 'user_id' in session

@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username."), ("test", "abcde", b"Incorrect password.")),
)
def test_login_validate_input(client, auth, username, password, message):
  with client:
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
  auth.login()
  with client:
    auth.logout()
    assert 'user_id' not in session