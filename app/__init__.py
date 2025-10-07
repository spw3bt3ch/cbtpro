import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from sqlalchemy import inspect, text

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User  # noqa: F401

    from .auth import auth_bp
    from .main import main_bp
    from .teacher import teacher_bp
    from .student import student_bp
    from .report import report_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(report_bp, url_prefix="/report")

    with app.app_context():
        db.create_all()
        try:
            inspector = inspect(db.engine)
            # question.time_limit_seconds
            q_cols = [c["name"] for c in inspector.get_columns("question")]
            if "time_limit_seconds" not in q_cols:
                db.session.execute(text("ALTER TABLE question ADD COLUMN time_limit_seconds INTEGER"))
                db.session.commit()
            # user.class_name
            u_cols = [c["name"] for c in inspector.get_columns("user")]
            if "class_name" not in u_cols:
                db.session.execute(text("ALTER TABLE user ADD COLUMN class_name VARCHAR(64)"))
                db.session.commit()
            # subject.class_name
            s_cols = [c["name"] for c in inspector.get_columns("subject")]
            if "class_name" not in s_cols:
                db.session.execute(text("ALTER TABLE subject ADD COLUMN class_name VARCHAR(64)"))
                db.session.commit()
        except Exception:
            pass

    return app
