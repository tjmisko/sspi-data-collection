from flask import Blueprint, render_template
from flask_login import login_required
from wtforms import Form, StringField, SelectField, validators

client_bp = Blueprint(
    'client_bp', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/home/static'
)

@client_bp.route('/')
def home():
    return render_template('home.html')

@client_bp.route('/about')
def about():
    return render_template('about.html')

@client_bp.route('/contact')
def contact():
    return render_template('contact.html')

@client_bp.route('/data')
def data():
    return render_template('data.html')

@client_bp.route('/indicators')
def indicators():
    return render_template('indicators.html')

@client_bp.route('/methodology')
def methodology():
    return render_template('methodology.html')