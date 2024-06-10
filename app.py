from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import signal
import sys
from bson import ObjectId


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/test_platform"

try:
    mongo = PyMongo(app)
    mongo.db.command('ping')  # Check if MongoDB server is reachable
except pymongo.errors.ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = mongo.db.admins.find_one({'username': username})
        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials"
    return render_template('admin_login.html')

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        mongo.db.admins.insert_one({'username': username, 'password': password})
        return redirect(url_for('admin_login'))
    return render_template('admin_signup.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('test'))
        else:
            return "Invalid credentials"
    return render_template('user_login.html')

@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        mongo.db.users.insert_one({'username': username, 'password': password})
        return redirect(url_for('user_login'))
    return render_template('user_signup.html')

@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/create_test', methods=['POST'])
def create_test():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    test_name = request.form.get('testName')
    time_limit = int(request.form.get('timeLimit'))
    no_tab_switch = 'noTabSwitch' in request.form
    webcam_access = 'webcamAccess' in request.form
    mongo.db.tests.insert_one({
        "name": test_name,
        "time_limit": time_limit,
        "no_tab_switch": no_tab_switch,
        "webcam_access": webcam_access
    })
    return redirect(url_for('dashboard'))

@app.route('/fetch_test_time', methods=['GET'])
def fetch_test_time():
    test_id = request.args.get('testId')
    test = mongo.db.tests.find_one({'_id': ObjectId(test_id)})
    if test:
        return str(test['time_limit'])
    else:
        return "Test not found", 404


@app.route('/test')
def test():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    return render_template('index.html')

@app.route('/add_question', methods=['POST'])
def add_question():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    question = {
        'test_id': request.form['testId'],
        'text': request.form['questionText'],
        'options': [
            request.form['option1'],
            request.form['option2'],
            request.form['option3'],
            request.form['option4']
        ],
        'correct_answer': request.form['correctAnswer']
    }
    mongo.db.questions.insert_one(question)
    return jsonify({'message': 'Question added successfully!'}), 200

@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    test_id = request.args.get('testId')
    questions_from_db = list(mongo.db.questions.find({"test_id": test_id}))
    for question in questions_from_db:
        question['_id'] = str(question['_id'])
    return jsonify(questions_from_db), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

@app.route('/finish.html')
def finish():
    return render_template('finish.html')

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(debug=True)
