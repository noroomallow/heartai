from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email address is already registered.", "danger")
            return render_template('register.html')

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.name
        flash("Registration successful! Welcome to HeartAI.", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash("Welcome back!", "success")
            return redirect(url_for('dashboard.index'))
        
        flash("Invalid email or password.", "danger")
        return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))