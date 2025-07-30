import os
import json
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

# Flask App Setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# PostgreSQL Config for Render
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://exercise_user:WtA49gw1Ng9hW3lPXtweOAqhdA1r10r1@dpg-d24vbrfgi27c73bggapg-a.oregon-postgres.render.com/exercise_db_irhs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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

# Load Dataset
def load_data():
    try:
        df = pd.read_csv('ExerciseDataset.csv')
        current_app.config['DATAFRAME'] = df
    except FileNotFoundError:
        print("Exercise dataset not found.")

# Home Page
@app.route('/')
@login_required
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        return render_template('home.html', user=user)
    flash("Invalid session. Please log in again.", "danger")
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.", "danger")

    return render_template('login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Recommend
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

    user = User.query.get(session['user_id'])

    return render_template("home.html", recommendations=recommendations, user=user)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You’ve been logged out.", "info")
    return redirect(url_for('login'))

# Cache Control
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# Run App
if __name__ == '__main__':
    with app.app_context():
        load_data()
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)



