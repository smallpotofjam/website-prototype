from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔑 Secret key for sessions
app.config['SECRET_KEY'] = 'super-secret-key-12345'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Create tables if not exist
with app.app_context():
    db.create_all()

# ----------------------
# Routes
# ----------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))  # ✅ Redirect after login
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

# Example pages
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/aarongame")
def aarongame():
    return render_template("aarongame.html")

# Category pages
@app.route("/coffee")
def coffee_page():
    return render_template("coffee.html")

@app.route("/fruit")
def fruit_page():
    return render_template("fruit.html")

@app.route("/meat")
def meat_page():
    return render_template("meat.html")

@app.route("/drinks")
def drinks_page():
    return render_template("drinks.html")

@app.route("/new")
def new_page():
    return render_template("new.html")

# ----------------------
if __name__ == "__main__":
    app.run(debug=True)