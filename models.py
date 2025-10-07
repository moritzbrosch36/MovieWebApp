from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user in the system.

    Attributes:
    id (int): Unique identifier for the user.
    name (str): Name of the user.
    movies (InstrumentedList of Movie):
        List-like relationship containing movies associated with the user.
    """

    __tablename__ = "user"

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
        title (str): Title of the movie (not nullable).
        year (int, optional): Release year of the movie.
        director (str, optional): Director of the movie.
        poster_url (str, optional): URL of the movie poster image.
        user_id (int): Foreign key referencing the associated user's ID.
    """
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    director = db.Column(db.String(200))
    poster_url = db.Column(db.String(500), nullable=True)

    # Connection to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        """Return a string representation of the Movie."""
        return f"<Movie {self.title} ({self.year})>"
