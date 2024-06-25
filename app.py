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
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    admin = mongo.db.admins.find_one({'username': username})
    if admin and check_password_hash(admin['password'], password):
        session['admin'] = username
        return jsonify({'success': True, 'redirect': url_for('admin')})
    else:
        return jsonify({'error': 'Invalid admin credentials, please try again.'}), 401

# Route for admin signup
@app.route('/admin_signup', methods=['POST'])
def admin_signup():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    hashed_password = generate_password_hash(password)
    mongo.db.admins.insert_one({'username': username, 'password': hashed_password})
    session['message'] = f"Admin account '{username}' successfully created. Please login."
    return jsonify({'success': True, 'message': session['message']}), 200

# Route for user login
@app.route('/user_login', methods=['POST'])
def user_login():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = mongo.db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        session['user'] = username
        return jsonify({'success': True, 'redirect': url_for('test')})
    else:
        return jsonify({'error': 'Invalid user credentials, please try again.'}), 401

# Route for user signup
@app.route('/user_signup', methods=['POST'])
def user_signup():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    hashed_password = generate_password_hash(password)
    mongo.db.users.insert_one({'username': username, 'password': hashed_password})
    session['message'] = f"User account '{username}' successfully created. Please login."
    return jsonify({'success': True, 'message': session['message']}), 200

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

    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    test_name = data.get('testName')
    time_limit = int(data.get('timeLimit'))
    no_tab_switch = data.get('noTabSwitch', False)
    webcam_access = data.get('webcamAccess', False)

    if not test_name or time_limit <= 0:
        return jsonify({'error': 'Invalid data provided'}), 400

    mongo.db.tests.insert_one({
        "name": test_name,
        "time_limit": time_limit,
        "no_tab_switch": no_tab_switch,
        "webcam_access": webcam_access
    })
    return jsonify({'success': True, 'message': 'Test created successfully!'}), 200

# Route to fetch test time
@app.route('/fetch_test_time', methods=['GET'])
def fetch_test_time():
    test_id = request.args.get('testId')
    test = mongo.db.tests.find_one({'_id': ObjectId(test_id)})
    if test:
        return jsonify({'time_limit': test['time_limit']}), 200
    else:
        return jsonify({'error': 'Test not found'}), 404

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

    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    question = {
        'test_id': data.get('testId'),
        'text': data.get('questionText'),
        'options': [
            data.get('option1'),
            data.get('option2'),
            data.get('option3'),
            data.get('option4')
        ],
        'correct_answer': data.get('correctAnswer')
    }

    if not all([question['test_id'], question['text'], question['options'], question['correct_answer']]):
        return jsonify({'error': 'Invalid data provided'}), 400

    mongo.db.questions.insert_one(question)
    return jsonify({'success': True, 'message': 'Question added successfully!'}), 200

# Route to fetch questions
@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    test_id = request.args.get('testId')
    if not test_id:
        return jsonify({'error': 'Missing testId'}), 400

    questions_from_db = list(mongo.db.questions.find({"test_id": test_id}))
    for question in questions_from_db:
        question['_id'] = str(question['_id'])
    return jsonify(questions_from_db)

# Route to submit test
@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'user' not in session:
        return redirect(url_for('user_login'))

    if request.content_type != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415

    data = request.json
    test_id = data.get('testId')
    answers = data.get('answers')

    if not test_id or not answers:
        return jsonify({'error': 'Missing testId or answers'}), 400

    questions = list(mongo.db.questions.find({"test_id": test_id}))
    if len(answers) != len(questions):
        return jsonify({'error': 'Invalid answers data provided'}), 400

    correct_answers = [question['correct_answer'] for question in questions]
    score = sum([1 for i in range(len(answers)) if answers[i] == correct_answers[i]])

    mongo.db.submissions.insert_one({
        "test_id": test_id,
        "user_id": session['user'],
        "score": score
    })
    return jsonify({'success': True, 'message': 'Test submitted successfully!'}), 200

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
