import secrets
import string
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import database as db # Import our new database module

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Needed for session management

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

# --- Flask Routes (Web Pages) ---

@app.route('/')
def home():
    """Renders the start page where users can choose to get a new code or use an existing one."""
    return render_template('start.html')

@app.route('/new-code')
def new_code():
    """
    Generates a new code for a new user and shows the message submission page.
    """
    user_code = generate_unique_code()
    db.create_user(user_code)
    return render_template('OuterCircleCode.html', code=user_code)

@app.route('/login', methods=['POST'])
def login():
    """Validates an existing user code and shows the message submission page."""
    code = request.form.get('user-code', '').upper()

    if code and db.code_exists(code):
        # If code is valid, show the submission page
        return render_template('OuterCircleCode.html', code=code)
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
    Admin-facing page to view all submitted messages.
    NOTE: In a production environment, this route should be protected
    with authentication and authorization.
    """
    all_messages = db.get_all_messages_grouped()

    # The data structure is now a flat list, so we need to group it for the template
    # This is a good candidate to move into a template filter or do in the template itself
    from itertools import groupby
    
    grouped_messages = {}
    for k, g in groupby(all_messages, lambda m: m['user_code']):
        grouped_messages[k] = list(g)

    return render_template('admin_view.html', messages_db=grouped_messages)

if __name__ == '__main__':
    # Initialize the database when the app starts
    db.init_db()
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run()
