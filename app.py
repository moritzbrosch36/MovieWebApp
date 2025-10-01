from flask import Flask, render_template, request, redirect, url_for
from models import db
from data_manager import DataManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moviewebapp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Comment out after first use
with app.app_context():
    db.create_all()

data_manager = DataManager(db.session)


# --- User Management ---
@app.route("/add_user", mehtods=["POST"])
def add_user():
    name = request.form["name"]
    data_manager.add_user(name)
    return redirect(url_for("list_users"))



