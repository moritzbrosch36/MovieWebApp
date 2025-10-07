import requests
import os
from dotenv import load_dotenv
from models import User, Movie

"""
DataManager
Handles user and movie data operations, including 
interactions with the OMDb API.
"""

# .env file loaded
load_dotenv()

class DataManager:
    """Manages database operations and external movie API requests."""

    def __init__(self, db_session):
        """
        Initialize DataManager with a database session and
        OMDb API configuration.
        """
        self.db_session = db_session
        self.api_key = os.getenv("API_KEY")
        self.omdb_url = os.getenv("OMDB_URL")

        if not self.api_key or not self.omdb_url:
            raise ValueError("OMDB_API_KEY or OMDB_URL is missing in the .env file!")

    # --- User Management ---
    def create_user(self, name):
        """Create a new user with the given name."""
        if not name.strip():
            return {"error": "Name cannot be empty."}

        new_user = User(name=name.strip())
        self.db_session.add(new_user)
        self.db_session.commit()
        return {"success": f"User '{name}' was created."}

    def get_users(self):
        """Retrieve all users."""
        return User.query.all()

    # --- Movie Management ---
    def get_movies(self, user_id):
        """Retrieve all movies for a given user."""
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, title, user_id):
        """Add a movie to the user's list using OMDb API data."""
        title = title.strip()
        if not title:
            return {"error": "Movie title must not be empty."}

        url = f"{self.omdb_url}?t={title}&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"Error connecting to OMDb API: {e}"}

        data = response.json()

        if data.get("Response") == "False":
            suggestions = self.search_movie_suggestions(title)
            return {
                "error": f"Movie '{title}' not found: {data.get('Error')}",
                "suggestions": suggestions
            }

        new_movie = Movie(
            title=data.get("Title", "Unknown"),
            year=data.get("Year", None),
            director=data.get("Director", "Unknown"),
            poster_url=data.get("Poster", ""),
            user_id=user_id
        )

        self.db_session.add(new_movie)
        self.db_session.commit()

        return {"success": f"Movie '{new_movie.title}' was added."}

    def update_movie(self, movie_id, new_title):
        """Update the title of an existing movie."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"error": f"Movie with ID {movie_id} does not exist."}

        new_title = new_title.strip()
        if not new_title:
            return {"error": "New movie title cannot be empty."}

        movie.title = new_title
        self.db_session.commit()
        return {"success": f"Movie changed to '{new_title}'."}

    def delete_movie(self, movie_id):
        """Delete a movie from the database."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"error": f"Movie with ID {movie_id} does not exist."}

        self.db_session.delete(movie)
        self.db_session.commit()
        return {"success": f"Movie '{movie.title}' was deleted."}

    def search_movie_suggestions(self, title):
        """Search for similar movie titles using the OMDb API."""
        url = f"{self.omdb_url}?s={title}&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return []

        data = response.json()
        if data.get("Response") == "True" and "Search" in data:
            return [movie.get("Title") for movie in data["Search"]]
        return []
