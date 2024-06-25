from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import signal
import sys

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/test_platform"

mongo = PyMongo(app)

# Route for dashboard
@app.route('/')
def dashboard():
    error = session.pop('error', None)  # Get and clear error message from session
    message = session.pop('message', None)  # Get and clear success message from session
    return render_template('dashboard.html', error=error, message=message)

# Route for admin login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.json['username']
    password = request.json['password']
    admin = mongo.db.admins.find_one({'username': username})
    if admin and check_password_hash(admin['password'], password):
        session['admin'] = username
        return jsonify({'success': True, 'redirect': url_for('admin')})
    else:
        return jsonify({'error': 'Invalid admin credentials, please try again.'})

# Route for admin signup
@app.route('/admin_signup', methods=['POST'])
def admin_signup():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    mongo.db.admins.insert_one({'username': username, 'password': password})
    session['message'] = f"Admin account '{username}' successfully created. Please login."
    return redirect(url_for('admin_login'))

# Route for user login
@app.route('/user_login', methods=['POST'])
def user_login():
    username = request.json['username']
    password = request.json['password']
    user = mongo.db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        session['user'] = username
        return jsonify({'success': True, 'edirect': url_for('test')})
    else:
        return jsonify({'error': 'Invalid user credentials, please try again.'})

# Route for user signup
@app.route('/user_signup', methods=['POST'])
def user_signup():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    mongo.db.users.insert_one({'username': username, 'password': password})
    session['message'] = f"User account '{username}' successfully created. Please login."
    return redirect(url_for('user_login'))

# Route for admin dashboard
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# Route to create a test
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

# Route to fetch test time
@app.route('/fetch_test_time', methods=['GET'])
def fetch_test_time():
    test_id = request.args.get('testId')
    test = mongo.db.tests.find_one({'_id': ObjectId(test_id)})
    if test:
        return str(test['time_limit'])
    else:
        return "Test not found", 404

# Route for user test
@app.route('/test')
def test():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    return render_template('index.html')

# Route to add a question
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

# Route to fetch questions
@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    test_id = request.args.get('testId')
    questions_from_db = list(mongo.db.questions.find({"test_id": test_id}))
    for question in questions_from_db:
        question['_id'] = str(question['_id'])
    return jsonify(questions_from_db)

# Route to submit test
@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    test_id = request.form['testId']
    answers = request.form.getlist('answers[]')
    correct_answers = []
    questions = list(mongo.db.questions.find({"test_id": test_id}))
    for question in questions:
        correct_answers.append(question['correct_answer'])
    score = sum([1 for i in range(len(answers)) if answers[i] == correct_answers[i]])
    mongo.db.submissions.insert_one({
        "test_id": test_id,
        "user_id": session['user'],
        "score": score
    })
    return jsonify({'message': 'Test submitted successfully!'})

# Route to fetch submissions
@app.route('/fetch_submissions', methods=['GET'])
def fetch_submissions():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    submissions_from_db = list(mongo.db.submissions.find())
    for submission in submissions_from_db:
        submission['_id'] = str(submission['_id'])
    return jsonify(submissions_from_db)

# Route to logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('user', None)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    app.run(debug=True)