from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db, User, Movie
import os
from datetime import datetime
from sqlalchemy import inspect

"""
MoviWebApp
A simple Flask web application for managing users and their favorite movies.
"""

# --- Flask App Setup ---
app = Flask(__name__)

# Use the existing movies.db in the current directory
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# --- Database Structure Verification ---
def verify_db_structure():
    """
    Checks if the 'user' and 'movie' tables exist in the database
    and whether the columns match the models.
    Prints warnings to the terminal if deviations are found.
    """
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\n🔍 Checking database structure...\n")

        expected_tables = {"user", "movie"}
        missing_tables = expected_tables - set(tables)
        if missing_tables:
            print(f"⚠️ Missing tables in movies.db: {missing_tables}")
        else:
            print("✅ All expected tables are present.")

        # Expected columns for both tables
        expected_columns = {
            "user": {"id", "name"},
            "movie": {"id", "title", "year", "director", "poster_url", "user_id"}
        }

        for table in expected_tables:
            if table not in tables:
                continue
            cols = {col["name"] for col in inspector.get_columns(table)}
            missing_cols = expected_columns[table] - cols
            extra_cols = cols - expected_columns[table]

            if missing_cols:
                print(f"⚠️ Table '{table}' is missing columns: {missing_cols}")
            if extra_cols:
                print(f"ℹ️ Table '{table}' contains extra columns: {extra_cols}")
            if not missing_cols and not extra_cols:
                print(f"✅ Table '{table}' structure is correct.")

        # Test the relationship (user → movie)
        try:
            test_user = db.session.query(User).first()
            if test_user:
                print(f"👤 Example user found: {test_user.name}")
                user_movies = db.session.query(Movie).filter_by(user_id=test_user.id).all()
                print(f"🎬 Associated movies: {[m.title for m in user_movies]}")
            else:
                print("⚠️ No users found in the database.")
        except Exception as e:
            print(f"❌ Error testing user-movie relationship: {e}")

        print("\n--- Database verification complete ---\n")


# --- Data Manager ---
with app.app_context():
    verify_db_structure()  # Automatically verify at startup
    data_manager = DataManager(db.session)

# --- Routes ---
@app.route("/")
def index():
    """Render the home page listing all users."""
    users = data_manager.get_users()
    return render_template("index.html", users=users)


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user from submitted form data."""
    name = request.form.get("name")
    result = data_manager.create_user(name)
    if "error" in result:
        return render_template("error.html", message=result["error"])
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def list_user_movies(user_id):
    """Display all movies for a given user."""
    user = db.session.get(User, user_id)
    if not user:
        return render_template("error.html",
                               message=f"User with ID {user_id} does not exist.")
    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", movies=movies, user=user)


@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id):
    """Add a new movie to the given user's movie list."""
    title = request.form.get("title")
    result = data_manager.add_movie(title, user_id)
    if "error" in result:
        return render_template("error.html",
                               message=result["error"],
                               suggestions=result.get("suggestions", []))
    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    """Update the title of a movie for the given user."""
    new_title = request.form.get("new_title")
    result = data_manager.update_movie(movie_id, new_title)
    if "error" in result:
        return render_template("error.html", message=result["error"])
    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Delete a movie from the given user's list."""
    result = data_manager.delete_movie(movie_id)
    if "error" in result:
        return render_template("error.html", message=result["error"])
    return redirect(url_for("list_user_movies", user_id=user_id))


@app.route("/about")
def about():
    """Render the about page."""
    return render_template("about.html")


# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors (page not found)."""
    return render_template("404.html",
                           message="Sorry, the page was not found."), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors (internal server errors)."""
    return render_template("500.html",
                           message="Something went wrong. Please try again later."), 500


@app.context_processor
def inject_year():
    """Inject the current year into all templates."""
    return {"year": datetime.now().year}


# --- Run App ---
if __name__ == "__main__":
    """Start the Flask application in debug mode."""
    app.run(debug=True)
