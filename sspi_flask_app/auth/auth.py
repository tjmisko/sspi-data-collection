from flask import Blueprint
from flask import current_app as app
from ..models.usermodel import User, db
from .. import login_manager, flask_bcrypt
from sqlalchemy_serializer import SerializerMixin
# load in the Flask class from the flask library
from flask import Flask, render_template, request, url_for, redirect
# load in the SQLAlchemy object to handle setting up the user data database
from flask_sqlalchemy import SQLAlchemy
# load in the UserMixin to handle the creation of user objects (not strictly necessary
# but it's a nice automation so we don't have to think too much about it)
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# load in the packages that make the forms pretty for submitting login and
# and restration data
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
# load in encryption library for passwords
from dataclasses import dataclass

auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# create a registration form for new users
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        # query the database to check whether the submitted new username is taken
        username_taken = User.query.filter_by(username=username.data).first()
        # if the username is taken, raise a validation ValidationError
        if username_taken:
            raise ValidationError("That username is already taken!")

# create a registration form for new users
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and flask_bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('home_bp.dashboard'))               
    return render_template('login.html', form=login_form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_bp.home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(register_form.password.data)
        new_user = User(username=register_form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html', form=register_form)
