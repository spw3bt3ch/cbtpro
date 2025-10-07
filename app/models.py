from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.STUDENT.value)
    class_name = db.Column(db.String(64))  # e.g., JSS1, SS2, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship("Subject", backref="teacher", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER.value

    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT.value


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    class_name = db.Column(db.String(64))  # Class this subject applies to
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship("Question", backref="subject", cascade="all,delete-orphan", lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    time_limit_seconds = db.Column(db.Integer, nullable=True)  # Optional per-question time limit

    options = db.relationship("Option", backref="question", cascade="all,delete-orphan", lazy=True)


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


class ExamSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    responses = db.relationship("Response", backref="session", cascade="all,delete-orphan", lazy=True)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("exam_session.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey("option.id"), nullable=False)


def nigeria_grade(score_percentage: float) -> str:
    if score_percentage >= 75:
        return "A1"
    if score_percentage >= 70:
        return "B2"
    if score_percentage >= 65:
        return "B3"
    if score_percentage >= 60:
        return "C4"
    if score_percentage >= 55:
        return "C5"
    if score_percentage >= 50:
        return "C6"
    if score_percentage >= 45:
        return "D7"
    if score_percentage >= 40:
        return "E8"
    return "F9"
