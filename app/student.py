from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from .models import Subject, Question, Option, ExamSession, Response, nigeria_grade
from . import db
from sqlalchemy import desc
from xhtml2pdf import pisa
from io import BytesIO

student_bp = Blueprint("student", __name__)


@student_bp.route("/")
@login_required
def index():
    if current_user.class_name:
        subjects = Subject.query.filter((Subject.class_name == None) | (Subject.class_name == current_user.class_name)).order_by(Subject.created_at.desc()).all()  # noqa: E711
    else:
        subjects = Subject.query.order_by(Subject.created_at.desc()).all()
    return render_template("student/index.html", subjects=subjects)


@student_bp.route("/report-card")
@login_required
def report_card():
    # Latest completed session per subject for current user
    subjects = Subject.query.all()
    rows = []
    total_scores = []
    for s in subjects:
        sess = (
            ExamSession.query
            .filter_by(subject_id=s.id, student_id=current_user.id)
            .filter(ExamSession.completed_at.isnot(None))
            .order_by(desc(ExamSession.completed_at))
            .first()
        )
        if not sess:
            continue
        questions = Question.query.filter_by(subject_id=s.id).all()
        total = len(questions)
        correct = 0
        for q in questions:
            resp = Response.query.filter_by(session_id=sess.id, question_id=q.id).first()
            sel = Option.query.get(resp.selected_option_id) if resp else None
            ans = Option.query.filter_by(question_id=q.id, is_correct=True).first()
            if sel and ans and sel.id == ans.id:
                correct += 1
        percentage = (correct / total * 100) if total else 0
        grade = nigeria_grade(percentage)
        rows.append({
            "subject": s,
            "session": sess,
            "total": total,
            "correct": correct,
            "percentage": percentage,
            "grade": grade,
        })
        total_scores.append(percentage)
    overall = sum(total_scores) / len(total_scores) if total_scores else 0
    overall_grade = nigeria_grade(overall)
    return render_template("student/report_card.html", rows=rows, overall=overall, overall_grade=overall_grade)


@student_bp.route("/report-card.pdf")
@login_required
def report_card_pdf():
    html = render_template("student/report_card_pdf.html", user=current_user)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf)
    if pisa_status.err:
        flash("Failed to generate PDF", "error")
        return redirect(url_for("student.report_card"))
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report_card.pdf'
    return response


@student_bp.route("/subjects/<int:subject_id>/start")
@login_required
def start_exam(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    existing = ExamSession.query.filter_by(subject_id=subject.id, student_id=current_user.id, completed_at=None).order_by(ExamSession.started_at.desc()).first()
    now = datetime.utcnow()
    new_session_needed = True
    if existing:
        end_time = existing.started_at + timedelta(minutes=subject.duration_minutes)
        if end_time > now:
            session = existing
            new_session_needed = False
    if new_session_needed:
        session = ExamSession(subject_id=subject.id, student_id=current_user.id, started_at=now)
        db.session.add(session)
        db.session.commit()
    return redirect(url_for("student.take_exam", session_id=session.id))


@student_bp.route("/sessions/<int:session_id>", methods=["GET", "POST"])
@login_required
def take_exam(session_id):
    session = ExamSession.query.get_or_404(session_id)
    if session.student_id != current_user.id:
        flash("Not authorized", "error")
        return redirect(url_for("student.index"))
    subject = Subject.query.get(session.subject_id)
    questions = Question.query.filter_by(subject_id=subject.id).all()

    if request.method == "POST":
        for q in questions:
            key = f"question_{q.id}"
            selected_option_id = request.form.get(key)
            if not selected_option_id:
                continue
            existing_resp = Response.query.filter_by(session_id=session.id, question_id=q.id).first()
            if existing_resp:
                existing_resp.selected_option_id = int(selected_option_id)
            else:
                db.session.add(Response(session_id=session.id, question_id=q.id, selected_option_id=int(selected_option_id)))
        session.completed_at = datetime.utcnow()
        db.session.commit()
        flash("Exam submitted", "success")
        return redirect(url_for("report.session_report", session_id=session.id))

    # Compute remaining seconds server-side to avoid client clock skew
    now = datetime.utcnow()
    end_time = session.started_at + timedelta(minutes=subject.duration_minutes)
    remaining_seconds = max(0, int((end_time - now).total_seconds()))

    # If session expired but no answers yet, reset start time and recompute
    if remaining_seconds == 0:
        has_answers = db.session.query(Response.id).filter_by(session_id=session.id).first() is not None
        if not has_answers:
            session.started_at = now
            db.session.commit()
            end_time = session.started_at + timedelta(minutes=subject.duration_minutes)
            remaining_seconds = max(0, int((end_time - datetime.utcnow()).total_seconds()))

    return render_template(
        "student/take_exam.html",
        subject=subject,
        questions=questions,
        session=session,
        end_remaining=remaining_seconds,
    )
