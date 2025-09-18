from flask import Flask, render_template
from datetime import datetime
import random

app = Flask(__name__, static_folder='static')


@app.route('/')
def home():
    return render_template('home.html', current_year=datetime.now().year)

@app.route('/aarongame')
def aarongame():
    different_index = random.randint(0, 8)

    # List of possible "different" images
    different_options = ['different.jpg', 'different1.jpg', 'different2.jpg', 'different3.jpg']
    chosen_different = random.choice(different_options)

    # Build the image grid
    images = ['base.jpg'] * 9
    images[different_index] = chosen_different

    return render_template('aarongame.html', images=images, different_index=different_index)




@app.route('/secondpage')
def secondpage():
    return render_template('secondpage.html', current_year=datetime.now().year)





@app.route('/dashboard')
def dashboard():
    user = "Morgan"
    notifications = [
        "New message from Chanya",
        "Server backup completed",
        "Update available for Flask"
    ]
    stats = {
        "projects": 3,
        "tasks": 12,
        "completed": 7
    }

    return render_template('dashboard.html', user=user, notifications=notifications, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)