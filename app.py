import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from functools import wraps

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  #  FIXED: Use environment or default

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'

# Initialize Extensions
bcrypt = Bcrypt(app)
mysql = MySQL(app)

#  FIXED: Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(" Checking session:", session)
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# WTForms Registration Form
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField("Register")

#  FIXED: Load Dataset Once
def load_data():
    try:
        df = pd.read_csv('ExerciseDataset.csv')
        current_app.config['DATAFRAME'] = df
        print("Dataset loaded successfully:", df.columns)
    except FileNotFoundError:
        print("Exercise dataset not found.")

#  FIXED: Home Page (Protected)
@app.route('/')
@login_required
def home():
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return render_template('home.html', user=user)
    flash("Invalid session. Please log in again.", "danger")
    return redirect(url_for('login'))

#  FIXED: Login Route validation authentication route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            stored_hash = user[3]
            if stored_hash and bcrypt.check_password_hash(stored_hash, password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                print(" Session after login:", session)
                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Incorrect password!", "danger")
        else:
            flash("No account found with this email.", "danger")

    return render_template('login.html')

#  FIXED: Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, hashed_pw))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

#  FIXED: Recommend (Protected)
@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    df = current_app.config.get('DATAFRAME')
    if df is None:
        flash("Dataset not loaded.", "danger")
        return redirect(url_for('home'))

    filters = {
        "Type": request.form.get('exercise_type'),
        "BodyPart": request.form.get('body_part'),
        "Equipment": request.form.get('equipment'),
        "Level": request.form.get('level'),
    }

    for key, value in filters.items():
        if value:
            df = df[df[key] == value]

    results = df[['Title', 'Description', 'Image']] if not df.empty else pd.DataFrame()
    recommendations = results.to_dict(orient='records')

    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    return render_template("home.html", recommendations=recommendations, user=user)

#  FIXED: Logout Route
@app.route('/logout')
def logout():
    session.clear()
    print(" Session after logout:", session)
    flash("You’ve been logged out.", "info")
    return redirect(url_for('login'))

#  FIXED: Prevent Back Navigation After Logout
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

#  Start the App
if __name__ == '__main__':
    with app.app_context():
        load_data()
    app.run(debug=True)

