from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        name (str): Name of the user.
        movies (list): List of movies associated with the user.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship: User can have multiple movies
    movies = db.relationship("Movie", backref="user", lazy=True)

    def __repr__(self):
        """Return a string representation of the User."""
        return f"<User {self.name}>"


class Movie(db.Model):
    """
    Represents a movie in the system.

    Attributes:
        id (int): Unique identifier for the movie.
        title (str): Title of the movie.
        genre (str): Genre of the movie.
        year (int): Release year of the movie.
        poster (str): URL of the movie poster image.
        user_id (int): ID of the associated user.
    """
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)
    poster = db.Column(db.String(500), nullable=True)

    # Connection to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        """Return a string representation of the Movie."""
        return f"<Movie {self.title} ({self.year})>"
