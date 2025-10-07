# CBTPro (Flask)

A simple CBT platform for schools with teacher content authoring, timed exams, and Nigeria-style grading reports. Styled with Tailwind CSS.

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

App runs at `http://127.0.0.1:5000`.

## Accounts
- Register as Teacher to create subjects, questions, and options.
- Register as Student to take CBT and view reports.

## Tech
- Flask, SQLAlchemy, Flask-Login, Flask-WTF
- Tailwind CSS via CDN
