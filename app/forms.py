from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional


CLASS_CHOICES = [(f"Primary {i}", f"Primary {i}") for i in range(1, 7)] \
    + [(f"JSS {i}", f"JSS {i}") for i in range(1, 4)] \
    + [(f"SS {i}", f"SS {i}") for i in range(1, 4)]
ALL_CLASS_CHOICES = [("", "All classes")] + CLASS_CHOICES


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role = SelectField("Role", choices=[("student", "Student"), ("teacher", "Teacher")], validators=[DataRequired()])
    class_name = SelectField("Class", choices=ALL_CLASS_CHOICES, validators=[Optional()])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField("Description")
    duration_minutes = IntegerField("Duration (minutes)", validators=[DataRequired(), NumberRange(min=5, max=300)])
    class_name = SelectField("Class", choices=ALL_CLASS_CHOICES, validators=[Optional()])
    submit = SubmitField("Save Subject")


class QuestionForm(FlaskForm):
    text = TextAreaField("Question Text", validators=[DataRequired(), Length(min=3)])
    time_limit_seconds = IntegerField("Per-question time (seconds)", validators=[Optional(), NumberRange(min=10, max=900)])
    submit = SubmitField("Save Question")


class OptionForm(FlaskForm):
    text = StringField("Option Text", validators=[DataRequired(), Length(min=1)])
    is_correct = BooleanField("Is Correct")
    submit = SubmitField("Add Option")


class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")


class ProfileForm(FlaskForm):
    class_name = SelectField("Class", choices=ALL_CLASS_CHOICES, validators=[Optional()])
    submit = SubmitField("Save Settings")
