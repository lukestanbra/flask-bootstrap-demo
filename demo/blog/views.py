from werkzeug.exceptions import abort

from flask import (
  Blueprint, flash, g, redirect, render_template, request, url_for
)

from demo import db
from demo.auth.views import login_required
from demo.blog.models import Post
from demo.blog.forms import UpdatePostForm

bp = Blueprint('blog', __name__)

@bp.route("/")
def index():
  posts = Post.query.order_by(Post.created.desc()).all()
  return render_template("blog/index.html", posts=posts)

def get_post(id, check_author=True):
  """Get a post and its author by id.
  Checks that the id exists and optionally that the current user is
  the author.
  :param id: id of post to get
  :param check_author: require the current user to be the author
  :return: the post with author information
  :raise 404: if a post with the given id doesn't exist
  :raise 403: if the current user isn't the author
  """
  post = Post.query.get_or_404(id, f"Post id {id} doesn't exist.")

  if check_author and post.author != g.user:
    abort(403)

  return post

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
  form = UpdatePostForm()
  if request.method == "POST" and form.validate_on_submit():
    title = form.title.data
    body = form.body.data
    error = None

    if not title:
      error = "Title is required."

    if error is not None:
      flash(error)
    else:
      db.session.add(Post(title=title, body=body, author=g.user))
      db.session.commit()
      return redirect(url_for("blog.index"))
  return render_template("blog/create.html", create_form=form)

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
  """Update a post if the current user is the author."""
  post = get_post(id)
  update_form = UpdatePostForm()
  if request.method == "GET":
    update_form.title.data = post.title
    update_form.body.data = post.body

  if request.method == "POST" and update_form.validate_on_submit():
    if update_form.delete.data:
      return redirect(url_for('blog.delete', id=id), code=307)
    title = update_form.title.data
    body = update_form.body.data
    error = None

    if not title:
      error = "Title is required."

    if error is not None:
      flash(error)
    else:
      post.title = title
      post.body = body
      db.session.commit()
      return redirect(url_for("blog.index"))

  return render_template("blog/update.html", post=post, update_form=update_form)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))