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
        if not name.strip():
            return {"error": "Name darf nicht leer sein."}

        new_user = User(name=name.strip())
        self.db_session.add(new_user)
        self.db_session.commit()
        return {"success": f"User '{name}' wurde erstellt."}

    def get_users(self):
        return User.query.all()

    # --- Movie Management ---
    def get_movies(self, user_id):
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, title, user_id):
        title = title.strip()
        if not title:
            return {"error": "Filmtitel darf nicht leer sein."}

        url = f"{self.omdb_url}?t={title}&apikey={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"Fehler bei der Verbindung zur OMDb API: {e}"}

        data = response.json()

        if data.get("Response") == "False":
            # Vorschläge suchen
            suggestions = self.search_movie_suggestions(title)
            return {
                "error": f"Film '{title}' nicht gefunden: {data.get('Error')}",
                "suggestions": suggestions
            }

        new_movie = Movie(
            title=data.get("Title", "Unknown"),
            genre=data.get("Genre", "Unknown"),
            year=data.get("Year", "Unknown"),
            user_id=user_id
        )

        self.db_session.add(new_movie)
        self.db_session.commit()

        return {"success": f"Film '{new_movie.title}' wurde hinzugefügt."}

    def update_movie(self, movie_id, new_title):
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"error": f"Film mit ID {movie_id} existiert nicht."}

        new_title = new_title.strip()
        if not new_title:
            return {"error": "Neuer Filmtitel darf nicht leer sein."}

        movie.title = new_title
        self.db_session.commit()
        return {"success": f"Film wurde auf '{new_title}' geändert."}

    def delete_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if not movie:
            return {"error": f"Film mit ID {movie_id} existiert nicht."}

        self.db_session.delete(movie)
        self.db_session.commit()
        return {"success": f"Film '{movie.title}' wurde gelöscht."}

    def search_movie_suggestions(self, title):
        """
        Suche ähnliche Filme über OMDb API.
        Gibt eine Liste mit Titeln zurück.
        """
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
