from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import SubjectForm, QuestionForm, OptionForm, DeleteForm
from .models import Subject, Question, Option
from . import db

teacher_bp = Blueprint("teacher", __name__)


def teacher_required():
    return current_user.is_authenticated and current_user.is_teacher()


@teacher_bp.before_request
def guard_teacher():
    allowed = {"teacher.index"}
    if request.endpoint and request.endpoint.split(":")[-1] in allowed:
        return None
    if not teacher_required():
        flash("Teacher access required", "error")
        return redirect(url_for("main.dashboard"))


@teacher_bp.route("/")
@login_required
def index():
    if not teacher_required():
        flash("Teacher access required", "error")
        return redirect(url_for("main.dashboard"))
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    delete_form = DeleteForm()
    return render_template("teacher/index.html", subjects=subjects, delete_form=delete_form)


@teacher_bp.route("/subjects/new", methods=["GET", "POST"])
@login_required
def create_subject():
    if not teacher_required():
        flash("Teacher access required", "error")
        return redirect(url_for("teacher.index"))
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data.strip(),
            description=form.description.data,
            duration_minutes=form.duration_minutes.data,
            class_name=form.class_name.data.strip() if form.class_name.data else None,
            teacher_id=current_user.id,
        )
        db.session.add(subject)
        db.session.commit()
        flash("Subject created", "success")
        return redirect(url_for("teacher.index"))
    return render_template("teacher/subject_form.html", form=form)


@teacher_bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data.strip()
        subject.description = form.description.data
        subject.duration_minutes = form.duration_minutes.data
        subject.class_name = form.class_name.data.strip() if form.class_name.data else None
        db.session.commit()
        flash("Subject updated", "success")
        return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
    return render_template("teacher/subject_form.html", form=form)


@teacher_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted", "info")
    return redirect(url_for("teacher.index"))


@teacher_bp.route("/subjects/<int:subject_id>")
@login_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    delete_form = DeleteForm()
    return render_template("teacher/subject_detail.html", subject=subject, delete_form=delete_form)


@teacher_bp.route("/subjects/<int:subject_id>/questions/new", methods=["GET", "POST"])
@login_required
def add_question(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = QuestionForm()
    if form.validate_on_submit():
        q = Question(subject_id=subject.id, text=form.text.data, time_limit_seconds=form.time_limit_seconds.data)
        db.session.add(q)
        db.session.commit()
        flash("Question added", "success")
        return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
    return render_template("teacher/question_form.html", form=form, subject=subject)


@teacher_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    subject = question.subject
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        question.text = form.text.data
        question.time_limit_seconds = form.time_limit_seconds.data
        db.session.commit()
        flash("Question updated", "success")
        return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
    return render_template("teacher/question_form.html", form=form, subject=subject)


@teacher_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    subject = question.subject
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted", "info")
    return redirect(url_for("teacher.subject_detail", subject_id=subject.id))


@teacher_bp.route("/questions/<int:question_id>/options/new", methods=["GET", "POST"])
@login_required
def add_option(question_id):
    question = Question.query.get_or_404(question_id)
    subject = question.subject
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = OptionForm()
    if form.validate_on_submit():
        option = Option(question_id=question.id, text=form.text.data, is_correct=form.is_correct.data)
        if form.is_correct.data:
            Option.query.filter_by(question_id=question.id, is_correct=True).update({"is_correct": False})
        db.session.add(option)
        db.session.commit()
        flash("Option added", "success")
        return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
    return render_template("teacher/option_form.html", form=form, question=question)


@teacher_bp.route("/options/<int:option_id>/edit", methods=["GET", "POST"])
@login_required
def edit_option(option_id):
    option = Option.query.get_or_404(option_id)
    question = option.question
    subject = question.subject
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = OptionForm(obj=option)
    if form.validate_on_submit():
        option.text = form.text.data
        if form.is_correct.data:
            Option.query.filter_by(question_id=question.id, is_correct=True).update({"is_correct": False})
        option.is_correct = form.is_correct.data
        db.session.commit()
        flash("Option updated", "success")
        return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
    return render_template("teacher/option_form.html", form=form, question=question)


@teacher_bp.route("/options/<int:option_id>/delete", methods=["POST"])
@login_required
def delete_option(option_id):
    option = Option.query.get_or_404(option_id)
    question = option.question
    subject = question.subject
    if subject.teacher_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("teacher.index"))
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(option)
        db.session.commit()
        flash("Option deleted", "info")
    return redirect(url_for("teacher.subject_detail", subject_id=subject.id))
