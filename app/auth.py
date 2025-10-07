from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from .forms import RegisterForm, LoginForm
from .models import User, UserRole
from . import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("Email already registered", "error")
            return redirect(url_for("auth.register"))
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower(),
            role=form.role.data,
            class_name=form.class_name.data.strip() if form.class_name.data else None,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid credentials", "error")
            return redirect(url_for("auth.login"))
        login_user(user)
        flash("Welcome back!", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.dashboard"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.home"))
