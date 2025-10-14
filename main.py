from flask import Flask, render_template,session
from datetime import datetime
import random
import os

import os.path as op

import logging



#set up logger

app_dir = op.realpath(os.path.dirname(__file__))

logger = logging.getLogger('app_logger')

logger.setLevel(logging.DEBUG)


#file handler for saving logs

log_file_path = op.join(app_dir, 'app.log')

handler = logging.FileHandler(log_file_path)

#format log messages

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)

#add handler to logger

logger.addHandler(handler)





app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Needed for session

@app.route('/')
def home():
    return render_template('home.html', current_year=datetime.now().year)

@app.errorhandler(404)

def page_not_found(e):

    logger.error('Page not found: %s', e)

    return render_template('404.html'), 404



@app.errorhandler(500)

def internal_error(error):

    logger.error('Internal Server Error: %s', error)

    db.session.rollback()  # reset DB session

    return render_template('500.html'), 500


@app.route('/aarongame')
def aarongame():
    # ⚡ Decide if it's a lightning round (1 in 15 chance)
    is_lightning_round = random.randint(1, 15) == 1

    # 🧠 Initialize variables
    images = []
    different_index = None
    different_indices = []
    zapped_zapper_index = None
    play_zap_animation = False

    if is_lightning_round:
        # ⚡ Lightning round: 4x4 grid, 3 unusual Aarons
        grid_size = 16
        images = ['base.jpg'] * grid_size
        different_options = ['different.jpg', 'different1.jpg', 'different2.jpg', 'different3.jpg']
        different_indices = random.sample(range(grid_size), 3)
        chosen_differents = random.sample(different_options, 3)
        for i, idx in enumerate(different_indices):
            images[idx] = chosen_differents[i]
    else:
        # 🔍 Normal round: 3x3 grid, 1 unusual Aaron
        grid_size = 9
        images = ['base.jpg'] * grid_size
        different_index = random.randint(0, grid_size - 1)
        different_options = ['different.jpg', 'different1.jpg', 'different2.jpg', 'different3.jpg']
        images[different_index] = random.choice(different_options)

        # 💰 Gold logic (1 in 10 chance)
        if random.randint(1, 10) == 1:
            gold_index = random.choice([i for i in range(grid_size) if i != different_index])
            images[gold_index] = random.choice(['gold.png', 'gold2.png'])

        # ⚡ Zapper logic (1 in 15 chance)
        if random.randint(1, 15) == 1:
            zapper_index = random.choice([i for i in range(grid_size) if images[i] == 'base.jpg'])
            images[zapper_index] = 'zapper.png'

        # ⚡ Zapper from previous round
        if session.get('zap_success'):
            zapped_zapper_index = session.pop('zapped_index', None)
            play_zap_animation = True
            session.pop('zap_success', None)
            if zapped_zapper_index is not None and images[zapped_zapper_index] == 'base.jpg':
                images[zapped_zapper_index] = 'zapper.png'

    return render_template('aarongame.html',
                           images=images,
                           is_lightning_round=is_lightning_round,
                           different_index=different_index,
                           different_indices=different_indices,
                           zapped_zapper_index=zapped_zapper_index,
                           play_zap_animation=play_zap_animation)



@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        user_entered = request.form['password']

        cur = connect.cursor()

        cur.execute(f"SELECT id, username, password from user WHERE username='{username}'")

        if cur is not None:

            # Get Stored hashed and salted password - Need to change fetch one to only return the one username

            #login_user(user)

            data = cur.fetchone()

            print(data)

            id = data[0]

            password = data[2]

            print("user id is ",id)

            print(password)

            print(type(password))

            # Compare Password with hashed password- Bcrypt

            if bcrypt.check_password_hash(password, user_entered):

                session['logged_in'] = True

                session['username'] = username

                session['id'] = id

                flash('You are now logged in', 'success')

                return redirect(url_for('welcome'))

                # Close Connection

                cursor.close()

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