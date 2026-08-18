from flask_wtf import FlaskForm

from wtforms import StringField

from wtforms import PasswordField

from wtforms import SubmitField

from wtforms.validators import DataRequired

from wtforms.validators import Email

class RegisterForm(FlaskForm):

    name = StringField("Name", validators=[DataRequired()])

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Register")