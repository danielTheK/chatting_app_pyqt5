import hashlib
import pickle

from flask import Flask, request, redirect, url_for, render_template, jsonify, session
from flask_socketio import SocketIO, send
import flask_socketio
USERS_PATH = 'users.pickle'
HISTORY_PATH = 'history.pickle'
FILE_ID_PATH = 'file-id.pickle'
FILES_PATH = 'files.pickle'


def get_users():
    try:
        with open(USERS_PATH, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        return {}


def update_users(new_users):
    with open(USERS_PATH, 'wb') as f:
        pickle.dump(new_users, f)


def reset_users():
    update_users({})


app = Flask(__name__)
app.secret_key = "sesdsd"
users = get_users()


@app.route('/')
def home():
    return redirect(url_for("login"))


@app.route('/login', methods=['POST', "GET"])
def login():
    if request.method == "GET":
        return render_template('index.html', title="Login")
    username = request.form['username']
    password = request.form['password']
    print(request)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if username in users and users[username] == hashed_password and username:
        # Redirect to the main app route upon successful login
        session["name"] = username
        return redirect(url_for('main_app'))
    else:
        # Add logic for failed login attempt, for example rendering a login failed page
        return redirect(url_for('home'))


@app.route('/main')
def main_app():
    if "name" in session:
        return render_template('main_app.html')
    else:
        return redirect(url_for("home"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@socketio.on('message')
def handle_message(message):
    messages.append(message)
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)



@app.route('/register', methods=['POST', "GET"])
def register():
    if request.method == "GET":
        return render_template('index.html', title="Register")
    else:
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if username in users:
            return render_template('index.html', title="Register")
        else:
            session["name"] = username
            users[username] = hashed_password
            update_users(users)
            return redirect(url_for('main_app'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
