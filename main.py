from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Dashboard page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/secondpage")
def secondpage():
    return render_template("secondpage.html")

@app.route("/aarongame")
def aarongame():
    return render_template("aarongame.html")

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

if __name__ == "__main__":
    app.run(debug=True)
