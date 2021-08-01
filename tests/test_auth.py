import pytest
from flask import g, session
from demo.auth.models import User

#  print(response.get_data(as_text=True))

def test_register(client, app, app_cxt):
  assert client.get("/auth/register").status_code == 200

  response = client.post(
    "/auth/register",
    data={"username": "abc", "password": "abc", "csrf_token": g.csrf_token}
  )
  assert "http://localhost/auth/login" == response.location

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
  assert client.get("/auth/register").status_code == 200
  response = client.post(
    "/auth/register", data={"username": username, "password": password, "csrf_token": g.csrf_token}
  )
  assert message in response.data

def test_login(client, app_cxt, auth):
  r = client.get("/auth/login")
  with client:
    response = auth.login(g.csrf_token)
    assert response.location == "http://localhost/"
    assert 'user_id' in session

@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username."), ("test", "abcde", b"Incorrect password.")),
)
def test_login_validate_input(client, app_cxt, auth, username, password, message):
  r = client.get("/auth/login")
  with client:
    response = auth.login(g.csrf_token, username, password)
    print(response.data)
    assert message in response.data

def test_logout(client, app_cxt, auth):
  r = client.get("/auth/login")
  response = auth.login(g.csrf_token)
  with client:
    auth.logout()
    assert 'user_id' not in session