import requests
import os
from dotenv import load_dotenv
from models import db, User, Movie

# .env Datei laden
load_dotenv()

class DataManager:
    def __init__(self, db_session):
        self.db_session = db_session
        self.api_key = os.getenv("API_KEY")
        self.omdb_url = os.getenv("OMDB_URL")

        if not self.api_key or not self.omdb_url:
            raise ValueError("OMDB_API_KEY or OMDB_URL is missing in the .env file!")

    # --- User Management ---
    def create_user(self, name):
        """Add a new user to the database."""
        new_user = User(name=name)
        self.db_session.add(new_user)
        self.db_session.commit()

    def get_users(self):
        """Return a list of all users in the database."""
        return User.query.all()

    # --- Movie Management ---
    def get_movies(self, user_id):
        """Return all movies of a specific user."""
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, title, user_id):
        """Add a new movie to a user's favorites using OMDb API."""
        url = f"{self.omdb_url}?t={title}&apikey={self.api_key}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Error retrieving data from OMDb API")

        data = response.json()

        if data.get("Response") == "False":
            raise ValueError(f"Movie '{title}' not found: {data.get('Error')}")

        new_movie = Movie(
            title=data.get("Title", "Unknown"),
            genre=data.get("Genre", "Unknown"),
            year=data.get("Year", "Unknown"),
            user_id=user_id
        )

        self.db_session.add(new_movie)
        self.db_session.commit()

    def update_movie(self, movie_id, new_title):
        """Update the title of a specific movie in the database."""
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = new_title
            self.db_session.commit()

    def delete_movie(self, movie_id):
        """Delete a movie from the user's favorites."""
        movie = Movie.query.get(movie_id)
        if movie:
            self.db_session.delete(movie)
            self.db_session.commit()
