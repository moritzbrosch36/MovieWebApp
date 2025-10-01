import requests
import os

from django.contrib.sites import requests
from dotenv import load_dotenv
from models import db, User, Movie

# Load .env file
load_dotenv()

class DataManager:
    def __init__(self, db_session):
        self.db_session = db_session
        self.api_key = os.getenv("OMDB_API_KEY")
        self.omdb_url = os.getenv("OMDB_URL")

        if not self.api_key or not self.omdb_url:
            raise ValueError("OMDB_API_KEY or OMDB_URL is missing in the .env file!")


    # --- User Management ---
    def add_user(self, name):
        new_user = User(name=name)
        self.db_session.add(new_user)
        self.db_session.commit()


    def get_all_users(self):
        return User.query.all()


    # --- Movie Management ---
    def add_movie(self, title, user_id):
        """Adds a movie by fetching info from OMDb API. """
        url = f"{self.omdb_url}?t={title}&apikey={self.api_key}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Error retrieving data from OMDb API.")

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


    def get_all_movies(self):
        return Movie.query.all()


    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            self.db_session.delete(movie)
            self.db_session.commit()


    def update_movie(self, movie_id, title, genre, year):
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = title
            movie.genre = genre
            movie.year = year
            self.db_session.commit()
