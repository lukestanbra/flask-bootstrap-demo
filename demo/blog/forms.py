from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class UpdatePostForm(FlaskForm):
  title = StringField("Title", validators=[DataRequired(), Length(1, 150)])
  body = TextAreaField("Body", validators=[DataRequired(), Length(1, 10_000)])
  submit = SubmitField('Submit')
  delete = SubmitField('Delete', render_kw={"onclick": "return confirm('Are you sure?');", "class": "btn btn-danger"})
