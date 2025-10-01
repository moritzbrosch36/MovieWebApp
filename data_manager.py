import requests
import os
import logging
from dotenv import load_dotenv
from models import db, User, Movie

# Load .env file
load_dotenv()

# Setup logger
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s %(levelname)s:%(message)s")


class DataManager:
    def __init__(self, db_session):
        self.db_session = db_session
        self.api_key = os.getenv("API_KEY")
        self.omdb_url = os.getenv("OMDB_URL")

        if not self.api_key or not self.omdb_url:
            logging.error("OMDB_API_KEY or OMDB_URL is missing in the .env file!")
            raise ValueError("OMDB_API_KEY or OMDB_URL is missing in the .env file!")

    # --- User Management ---
    def create_user(self, name):
        if not name.strip():
            return {"error": "Name cannot be empty."}

        try:
            new_user = User(name=name.strip())
            self.db_session.add(new_user)
            self.db_session.commit()
            return {"success": f"User '{name}' created successfully."}
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error creating user '{name}': {str(e)}")
            return {"error": f"Database error while creating user: {str(e)}"}

    def get_users(self):
        try:
            return User.query.all()
        except Exception as e:
            logging.error(f"Error retrieving users: {str(e)}")
            return []

    # --- Movie Management ---
    def get_movies(self, user_id):
        try:
            return Movie.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logging.error(f"Error retrieving movies for user {user_id}: {str(e)}")
            return []

    def add_movie(self, title, user_id):
        title = title.strip()
        if not title:
            return {"error": "Movie title cannot be empty."}

        try:
            url = f"{self.omdb_url}?t={title}&apikey={self.api_key}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"OMDb API request failed for '{title}': {str(e)}")
            return {"error": f"Error connecting to OMDb API: {str(e)}"}

        data = response.json()

        if data.get("Response") == "False":
            suggestions = self.search_movie_suggestions(title)
            return {
                "error": f"Movie '{title}' not found: {data.get('Error')}",
                "suggestions": suggestions
            }

        try:
            new_movie = Movie(
                title=data.get("Title", "Unknown"),
                genre=data.get("Genre", "Unknown"),
                year=data.get("Year", "Unknown"),
                user_id=user_id
            )
            self.db_session.add(new_movie)
            self.db_session.commit()
            return {"success": f"Movie '{new_movie.title}' added successfully."}
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error adding movie '{title}': {str(e)}")
            return {"error": f"Database error while adding movie: {str(e)}"}

    def update_movie(self, movie_id, new_title):
        if not new_title.strip():
            return {"error": "New title cannot be empty."}

        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return {"error": f"Movie with ID {movie_id} does not exist."}
            movie.title = new_title.strip()
            self.db_session.commit()
            return {"success": f"Movie updated to '{new_title}'."}
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error updating movie ID {movie_id}: {str(e)}")
            return {"error": f"Database error while updating movie: {str(e)}"}

    def delete_movie(self, movie_id):
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return {"error": f"Movie with ID {movie_id} does not exist."}
            self.db_session.delete(movie)
            self.db_session.commit()
            return {"success": f"Movie '{movie.title}' deleted successfully."}
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Error deleting movie ID {movie_id}: {str(e)}")
            return {"error": f"Database error while deleting movie: {str(e)}"}

    def search_movie_suggestions(self, title):
        try:
            url = f"{self.omdb_url}?s={title}&apikey={self.api_key}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return []

        data = response.json()
        if data.get("Response") == "True" and "Search" in data:
            return [movie.get("Title") for movie in data["Search"]]
        return []
