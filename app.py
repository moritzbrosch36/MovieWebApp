from flask import Flask, request, redirect, url_for, render_template
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
    """Homepage: List of all users + form to add a user."""
    users = data_manager.get_users()
    return render_template("home.html", users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """POST: Add new user and redirect to '/'."""
    name = request.form.get("name")
    if name:
        data_manager.create_user(name)
    return redirect(url_for("home"))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_user_movies(user_id):
    """GET: Display a user's list of movies."""
    movies = data_manager.get_movies(user_id)
    user = User.query.get(user_id)
    return render_template("movie.html", movies=movies, user=user)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    title = request.form.get("title")
    if title:
        data_manager.add_movie(title, user_id)
    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """POST: Update a movie title."""
    new_title = request.form.get("new_title")
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """POST: Delete a user's movie."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for("list_user_movies", user_id=user_id))


# --- Run App ---
if __name__ == '__main__':
    """
    Only use once at the start.
    with app.app_context():
        db.create_all()
    """
    app.run(debug=True)




