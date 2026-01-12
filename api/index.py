"""
Vercel serverless function entry point
This file makes your Flask app compatible with Vercel's serverless architecture
"""
import os
import sys

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, static_folder='../src/static', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nfc_attendance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CORS
CORS(app)

# Import and initialize database
from src.models import db, Student, Attendance, Faculty
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Register blueprints (modular approach - better for serverless)
from src.api.students import students_bp
from src.api.nfc import nfc_bp
from src.api.attendance import attendance_bp
from src.api.faculty import faculty_bp

app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(nfc_bp, url_prefix='/api/nfc')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(faculty_bp, url_prefix='/api/faculty')

# Frontend routes
@app.route('/')
def index():
    return send_from_directory('../src/static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('../src/static', path)
    except:
        return send_from_directory('../src/static', 'index.html')

# Vercel expects a variable named 'app' or 'application'
# This is the CRITICAL part for serverless deployment
handler = app

# For local development
if __name__ == '__main__':
    app.run(debug=True)
