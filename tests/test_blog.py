import pytest

from flask import g, session, url_for
from demo import db
from demo.auth.models import User
from demo.blog.models import Post


def test_index(client, auth):
  with client:
    response = client.get(url_for("blog.index"))
    assert b"Log In" in response.data
    assert b"Register" in response.data

    response = auth.login()
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert f"href=\"{url_for('blog.update', id=1)}\"".encode('utf-8') in response.data


@pytest.mark.parametrize(
  ("get", "post", "kwargs"),
  (
    ("blog.create","blog.create", {}),
    ("blog.update","blog.update", {"id": 1}),
    ("blog.update","blog.delete", {"id": 1})
  )
)
def test_login_required(client, app, get, post, kwargs):
  LOGIN_URL=f"http://localhost{url_for('auth.login')}"
  with client:
    response = client.get(url_for(get, **kwargs))
    assert response.location == LOGIN_URL
    response = client.post(url_for(post, **kwargs), follow_redirects=True)
    if app.config.get('WTF_CSRF_ENABLED'):
      assert response.status_code == 400
    else:
      assert response.history[0].location == LOGIN_URL

def test_author_required(client, app, app_cxt, auth):
  with client:
    # change the post author to another user
    with app.app_context():
      Post.query.get(1).author = User.query.get(2)
      db.session.commit()
    r1 = auth.login()
    r2 = client.get(url_for('blog.update', id=1))
    r3 = client.post(
      url_for('blog.update', id=1),
      data={"title": "foo", "body": "bar", "csrf_token": g.get('csrf_token')},
      follow_redirects=True
    )
    assert r3.status_code == 403
    assert client.post(url_for('blog.delete', id=1)).status_code == 403
    # current user doesn't see edit link
    assert f"href=\"{url_for('blog.update', id=1)}\"".encode('utf-8') not in client.get('/').data

@pytest.mark.parametrize(
  ("path", "id"),
  (
    ("blog.update", 2),
    ("blog.delete", 2)
  )
)
def test_exists_required(client, app_cxt, auth, path, id):
  auth.login()
  assert client.post(
    url_for(path, id=id),
    data={"csrf_token": g.get("csrf_token")}
  ).status_code == 404

def test_create(client, auth, app):
  auth.login()
  assert client.get(url_for("blog.create")).status_code == 200
  client.post(
    url_for("blog.create"),
    data={"title": "created", "body": "created", "csrf_token": g.get('csrf_token')}
  )

  with app.app_context():
    assert Post.query.count() == 2

def test_update(client, auth, app):
  auth.login()
  assert client.get(url_for("blog.update", id=1)).status_code == 200
  client.post(
    url_for("blog.update", id=1),
    data={"title": "updated", "body": "updated", "csrf_token": g.get('csrf_token')}
  )

  with app.app_context():
    assert Post.query.get(1).title == "updated"

@pytest.mark.parametrize(
  ("path", "kwargs"),
  (
    ("blog.create", {}),
    ("blog.update", {"id": 1})
  )
)
def test_create_update_validate(client, auth, path, kwargs):
  auth.login()
  response = client.post(
    url_for(path, **kwargs),
    data={"title": "", "body": "", "csrf_token": g.get('csrf_token')}
  )
  assert b"This field is required." in response.data


def test_delete(client, auth, app):
  auth.login()
  response = client.post(
    url_for("blog.delete", id=1),
    data = {"csrf_token": g.get('csrf_token')}
  )
  assert response.headers["Location"] == "http://localhost/"

  with app.app_context():
    assert Post.query.get(1) is None