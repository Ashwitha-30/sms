
# Quick start
# 1) pip install flask flask_sqlalchemy werkzeug
# 2) python app.py --init-db   # creates DB and optional seed admin
# 3) python app.py             # run server at http://127.0.0.1:8080

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from flask import Response
import csv
from io import StringIO

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    mark = db.Column(db.Integer, nullable=False)

    student = db.relationship('Student', backref='marks', lazy=True)
    course = db.relationship('Course', backref='marks', lazy=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password_raw = request.form.get('password', '')
        if not username or not password_raw:
            flash('Username and password required')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        password = generate_password_hash(password_raw)
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful, please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('dashboard.html', students=students)

@app.route('/students')
def students_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('students.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if not name or not email:
        flash('Name and email required')
        return redirect(url_for('students_view'))
    if Student.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('students_view'))
    student = Student(name=name, email=email)
    db.session.add(student)
    db.session.commit()
    flash('Student added')
    return redirect(url_for('students_view'))

@app.route('/courses')
def courses_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    courses = Course.query.order_by(Course.id.desc()).all()
    return render_template('courses.html', courses=courses)

@app.route('/add_course', methods=['POST'])
def add_course():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form.get('title', '').strip()
    if not title:
        flash('Course title required')
        return redirect(url_for('courses_view'))
    if Course.query.filter_by(title=title).first():
        flash('Course already exists')
        return redirect(url_for('courses_view'))
    course = Course(title=title)
    db.session.add(course)
    db.session.commit()
    flash('Course added')
    return redirect(url_for('courses_view'))

@app.route('/marks')
def marks_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    marks = Mark.query.all()
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('marks.html', marks=marks, students=students, courses=courses)

@app.route('/add_mark', methods=['POST'])
def add_mark():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        student_id = int(request.form.get('student_id'))
        course_id = int(request.form.get('course_id'))
        mark_val = int(request.form.get('mark'))
    except (TypeError, ValueError):
        flash('Please select student, course and a valid mark')
        return redirect(url_for('marks_view'))

    if not Student.query.get(student_id) or not Course.query.get(course_id):
        flash('Invalid student or course')
        return redirect(url_for('marks_view'))

    new_mark = Mark(student_id=student_id, course_id=course_id, mark=mark_val)
    db.session.add(new_mark)
    db.session.commit()
    flash('Mark added')
    return redirect(url_for('marks_view'))

@app.route('/download_marks')
def download_marks():
    # Query all marks
    marks = Mark.query.all()

    # Prepare CSV in memory
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Course', 'Marks'])
    for m in marks:
        cw.writerow([m.student.name, m.course.title, m.mark])  # <-- fixed

    # Return as downloadable file
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=marks_report.csv"
    return output


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if '--init-db' in sys.argv:
            # Create a demo admin if none exists
            if not User.query.filter_by(username='admin').first():
                demo = User(username='admin', password=generate_password_hash('admin123'))
                db.session.add(demo)
                db.session.commit()
                print('Created default admin: admin / admin123')
    # Only run the server if not called with --init-db only
    if '--init-db' not in sys.argv or len(sys.argv) == 1:
        app.run(debug=True, port=8080)


