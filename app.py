from flask import Flask
from data_manager import DataManager
from models import db, User, Movie
import os

# --- Flask App Setup ---
app = Flask(__name__)

# Create database path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create DataManager object (pass db.sessions)
data_manager = DataManager(db.session)

# --- Routes ---
@app.route('/')
def home():
    return "Welcome to MoviWeb App!"

# Example route: Show all users
@app.route('/users')
def get_users():
    users = data_manager.get_users()
    return {u.id: u.name for u in users}

# Example route: Show all movies of a user
@app.route('/users/<int:user_id>/movies')
def get_user_movies(user_id):
    movies = data_manager.get_movies(user_id)
    return {m.id: f"{m.title} ({m.year})" for m in movies}

# --- Run App ---
if __name__ == '__main__':
    """
    Only use once at the start.
    with app.app_context():
        db.create_all()
    """
    app.run(debug=True)




