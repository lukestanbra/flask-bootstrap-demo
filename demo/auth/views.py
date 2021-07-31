from demo.auth.forms import LoginForm
import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from demo import db
from demo.auth.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
  """View decorator that redirects anonymous users to the login page."""

  @functools.wraps(view)
  def wrapped_view(**kwargs):
      if g.user is None:
          return redirect(url_for("auth.login"))

      return view(**kwargs)

  return wrapped_view


@bp.before_app_request
def load_logged_in_user():
  """If a user id is stored in the session, load the user object from
  the database into ``g.user``."""
  user_id = session.get("user_id")
  g.user = User.query.get(user_id) if user_id is not None else None


@bp.route('/register', methods=('GET', 'POST'))
def register():
  form = LoginForm()
  if request.method == "POST" and form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    error = None

    if not username:
      error = "Username is required."
    elif not password:
      error = "Password is required."
    elif db.session.query(
      User.query.filter_by(username=username).exists()
    ).scalar():
      error = f"User {username} is already registered."

    if error is None:
      db.session.add(User(username=username, password=password))
      db.session.commit()
      return redirect(url_for("auth.login"))

    flash(error)

  return render_template("auth/register.html", register_form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
  """Log in a registered user by adding the user id to the session."""
  form = LoginForm()
  if request.method == "POST" and form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    error = None
    user = User.query.filter_by(username=username).first()

    if user is None:
      error = "Incorrect username."
    elif not user.check_password(password):
      error = "Incorrect password."

    if error is None:
      # store the user id in a new session and return to the index
      session.clear()
      session["user_id"] = user.id
      return redirect(url_for("index"))

    flash(error)

  return render_template("auth/login.html", login_form=form)

@bp.route("/logout")
def logout():
  """Clear the current session, including the stored user id."""
  session.clear()
  return redirect(url_for("index"))
