from dotenv import load_dotenv  # Import the load_dotenv function

# Load environment variables from a .env file.
# This must be done before other imports that rely on environment variables.
load_dotenv()

import os
import secrets
import string
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

import database as db  # Import our new database module

# --- Configuration ---
CODE_LENGTH = 4
CODE_CHARS = string.ascii_uppercase + string.digits

# --- Core Logic ---

def generate_unique_code(): #It runs in a loop to ensure the generated code is unique (not already a key in the existing database).
    """Generates a unique code that is not already in use."""
    while True:
        new_code = ''.join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
        if not db.code_exists(new_code):
            return new_code

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Register database functions with the app. This also handles teardown.
    db.init_app(app)

    # --- Flask Routes (Web Pages) ---
    @app.route('/')
    def home():
        """Renders the start page, displaying an error message if one is provided."""
        error_message = request.args.get('error')
        return render_template('start.html', error=error_message)

    @app.route('/new-code')
    def new_code():
        """
        Generates a new code for a new user and shows the message submission page.
        """
        user_code = generate_unique_code()
        db.create_user(user_code)
        return render_template('OuterCircleCode.html', code=user_code)

    @app.route('/submit/<string:code>')
    def show_submit_page(code):
        """Shows the message submission page for a given valid code."""
        if db.code_exists(code):
            return render_template('OuterCircleCode.html', code=code)
        else:
            # If the code in the URL is invalid, redirect to the home page with an error.
            return redirect(url_for('home', error="Invalid code. Please try again or get a new one."))

    @app.route('/login', methods=['POST'])
    def login():
        """Validates an existing user code and shows the message submission page."""
        code = request.form.get('user-code', '').upper()

        if code and db.code_exists(code):
            # If code is valid, redirect to the submission page for that code.
            return redirect(url_for('show_submit_page', code=code))
        else:
            # If code is invalid, show the start page again with an error
            return render_template('start.html', error="Invalid code. Please try again or get a new one.")

    @app.route('/submit-message', methods=['POST'])
    def submit_message():
        """
        Handles the form submission.
        """
        # Get data from the submitted form
        code = request.form.get('user-code', '').upper()
        message_text = request.form.get('anon-message')
        sensitivity = request.form.get('sensitivity')
        delivery = request.form.get('delivery')

        # Basic validation
        # Check if the code exists in our new database
        if not code or not db.code_exists(code):
            return render_template('Error.html'), 400
        if not message_text:
            return "Error: Message cannot be empty.", 400

        # Create a message object
        new_message = {
            "message": message_text,
            "sensitivity": sensitivity,
            "delivery": delivery,
            "timestamp_utc": datetime.utcnow().isoformat()
        }

        # Add the message to the database
        db.add_message_for_code(code, new_message)
        # Render the encouragement page, passing the user's code back.
        return render_template('EncouragementPage.html', code=code)

    @app.route('/messages')
    def view_messages():
        """
        Page to view all submitted messages.
        """
        all_messages = db.get_all_messages_grouped()
        return render_template('admin_view.html', messages=all_messages)

    return app

if __name__ == '__main__':
    # This block allows you to run the app directly with `python app.py`
    # for local development.
    app = create_app()
    # The waitress server is for production; for development, app.run() is great.
    app.run(debug=True, port=5001)
