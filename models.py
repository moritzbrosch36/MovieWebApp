from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship: User can have multiple movies
    movies = db.relationship("Movie", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.Integer)

    # Connection to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Movie {self.title} ({self.year}"


