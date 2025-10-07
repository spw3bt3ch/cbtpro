from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Subject
from .forms import ProfileForm
from . import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    subjects = Subject.query.order_by(Subject.created_at.desc()).limit(4).all()
    return render_template("home.html", subjects=subjects)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ProfileForm(class_name=current_user.class_name or "")
    if form.validate_on_submit():
        current_user.class_name = form.class_name.data or None
        db.session.commit()
        flash("Settings saved", "success")
        return redirect(url_for("main.settings"))
    return render_template("settings.html", form=form)


@main_bp.route("/contact")
def contact():
    return render_template("contact.html")
