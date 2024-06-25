# Demo Project

## Description

This is a demo project for a web application built with Flask and MongoDB. The application includes admin and user login/signup functionalities, along with a dashboard and other related features.

## Project Structure

- **app.py**: The main Python script that runs the server and handles the routing for the web application.
- **templates/**: A directory containing HTML templates used by the web application.

## Prerequisites

To run this project, you will need:

- **Python 3.x**
- **Flask**
- **Flask-PyMongo**
- **MongoDB**

## Installation

1. **Clone the repository or extract the zip file**:

   
   unzip demo-main.zip
   cd demo-main/demo-main
Create a virtual environment (optional but recommended):


python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
Install the required packages:


pip install flask flask-pymongo werkzeug
Set up MongoDB:
Ensure you have MongoDB installed and running. You can download and install MongoDB from the official MongoDB website.

Update the MongoDB URI:
Ensure the MongoDB URI in app.py is correctly set to your MongoDB server. By default, it is set to mongodb://localhost:27017/test_platform.

# Usage
Run the application:


python app.py
Open your web browser and navigate to http://127.0.0.1:5000 to see the web application in action.

# File Descriptions
app.py: Contains the Flask application setup, route definitions, and functions to render the templates.

Routes include:
/: Dashboard page.
/admin_login: Admin login page (GET/POST).
/admin_signup: Admin signup page (GET/POST).
/user_login: User login page (GET/POST).
templates/admin.html: HTML template for the admin page.

templates/admin_login.html: HTML template for the admin login page.

templates/admin_signup.html: HTML template for the admin signup page.

templates/dashboard.html: HTML template for the dashboard page.

templates/finish.html: HTML template for the finish page.

templates/index.html: HTML template for the home page.

templates/user_login.html: HTML template for the user login page.

templates/user_signup.html: HTML template for the user signup page.

# Contributing
If you wish to contribute to this project, please fork the repository and create a pull request with your changes. Ensure that your code adheres to the existing coding style and conventions.

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Acknowledgements
This project uses Flask for building the web application.
This project uses Flask-PyMongo for MongoDB integration.
