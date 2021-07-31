from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from wtforms.fields import StringField, PasswordField, SubmitField

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
  password = PasswordField('Password', validators=[DataRequired(), Length(3, 150)])
  submit = SubmitField()