from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db, User, Movie
import os

# --- Flask App Setup ---
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

data_manager = DataManager(db.session)

# --- Routes ---

@app.route('/')
def index():
    """Display list of all users."""
    users = data_manager.get_users()
    return render_template('index.html',
                           users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user and redirect to index."""
    name = request.form.get("name")
    result = data_manager.create_user(name)

    if "error" in result:
        return render_template("error.html",
                               message=result["error"])

    return redirect(url_for("index"))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_user_movies(user_id):
    """Display all movies for a given user."""
    user = User.query.get(user_id)

    if not user:
        return render_template("error.html",
                               message=f"User with ID {user_id} does not exist.")

    movies = data_manager.get_movies(user_id)
    return render_template("movies.html",
                           movies=movies, user=user)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a movie to the user's favorites."""
    title = request.form.get("title")
    result = data_manager.add_movie(title, user_id)

    if "error" in result:
        return render_template("error.html",
                               message=result["error"],
                               suggestions=result.get("suggestions", []))

    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update',
           methods=['POST'])
def update_movie(user_id, movie_id):
    """Update movie title."""
    new_title = request.form.get("new_title")
    result = data_manager.update_movie(movie_id, new_title)

    if "error" in result:
        return render_template("error.html",
                               message=result["error"])

    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie from user's favorites."""
    result = data_manager.delete_movie(movie_id)

    if "error" in result:
        return render_template("error.html",
                               message=result["error"])

    return redirect(url_for("list_user_movies", user_id=user_id))


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
