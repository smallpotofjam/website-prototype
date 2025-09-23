from flask import Flask, render_template,session
from datetime import datetime
import random

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Needed for session

@app.route('/')
def home():
    return render_template('home.html', current_year=datetime.now().year)

@app.route('/aarongame')
def aarongame():
    different_index = random.randint(0, 8)
    different_options = ['different.jpg', 'different1.jpg', 'different2.jpg', 'different3.jpg']
    chosen_different = random.choice(different_options)

    images = ['base.jpg'] * 9
    images[different_index] = chosen_different

    # Gold logic (1 in 10 chance)
    if random.randint(1, 10) == 1:
        gold_index = random.choice([i for i in range(9) if i != different_index])
        gold_type = random.choice(['gold.png', 'gold2.png'])
        images[gold_index] = gold_type

    # Zapper logic (1 in 15 chance)
    if random.randint(1, 5) == 1:
        zapper_index = random.choice([i for i in range(9) if images[i] == 'base.jpg'])
        images[zapper_index] = 'zapper.png'

    # Check if a zapper was zapped last round
    zapped_zapper_index = None
    play_zap_animation = False

    if session.get('zap_success'):
        zapped_zapper_index = session.pop('zapped_index', None)
        play_zap_animation = True
        session.pop('zap_success', None)

        # Ensure the image is set to zapper
        if zapped_zapper_index is not None and images[zapped_zapper_index] == 'base.jpg':
            images[zapped_zapper_index] = 'zapper.png'
    else:
        zapped_zapper_index = None
        play_zap_animation = False

    return render_template(
        'aarongame.html',
        images=images,
        different_index=different_index,
        zapped_zapper_index=zapped_zapper_index,
        play_zap_animation=play_zap_animation
    )

@app.route('/save_zapped/<int:index>')
def save_zapped(index):
    session['zapped_index'] = index
    session['zap_success'] = True
    return '', 204

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