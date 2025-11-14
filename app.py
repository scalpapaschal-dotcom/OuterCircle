import secrets
import string
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
from dal import messages_dal # Import our new Data Access Layer for messages

# Load environment variables from a .env file for local development
load_dotenv()

# --- Flask App Initialization ---
app = Flask(__name__)
auth = HTTPBasicAuth()

# --- Admin Credentials from Environment Variables ---
# For security, we load the admin username and password from environment variables.
# You will need to set these in your Render dashboard.
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# --- Configuration ---
CODE_LENGTH = 4
CODE_CHARS = string.ascii_uppercase + string.digits

# --- Authentication Logic ---

@auth.verify_password
def verify_password(username, password):
    """Checks if the provided username and password are correct."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return username

# --- Core Logic ---

def generate_unique_code(): #It runs in a loop to ensure the generated code is unique (not already a key in the existing database).
    """Generates a unique code that is not already in use."""
    while True:
        # This function needs to be updated to check against the new database.
        # For now, we will assume it works, but this is a placeholder for a new DAL function.
        new_code = ''.join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
        # if not codes_dal.code_exists(new_code): # You would create this function
        return new_code # Temporarily just return a code

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
    # In a real app, you would save this code to a 'users' or 'codes' table
    # e.g., codes_dal.create_code(user_code)
    return render_template('OuterCircleCode.html', code=user_code)

@app.route('/login', methods=['POST'])
def login():
    """Validates an existing user code and shows the message submission page."""
    code = request.form.get('user-code', '').upper()
    # This logic needs to be updated to check the database via a DAL function.
    # e.g., if code and codes_dal.code_exists(code):
    if code and db.code_exists(code):
        # If code is valid, show the submission page
        return render_template('OuterCircleCode.html', code=code)
    else:
        # If code is invalid, show the start page again with an error
        return render_template('start.html', error="Invalid code. Please try again or get a new one.")

@app.route('/continue-with-code', methods=['POST'])
def continue_with_code():
    """
    Allows a user to continue to the message submission page directly from another page,
    like the encouragement page, without re-validating the code input.
    """
    code = request.form.get('user-code')
    return render_template('OuterCircleCode.html', code=code)

@app.route('/submit-message', methods=['POST'])
def submit_message():
    """
    Handles the form submission.
    """
    # Get data from the submitted form. Let's assume 'name' and 'email' for now.
    name = request.form.get('name') # Assuming you add a 'name' field to your form
    email = request.form.get('email') # Assuming you add an 'email' field
    message_text = request.form.get('message')

    # Basic validation
    if not message_text:
        # You would handle this error appropriately, maybe render the form again with an error
        return "Message cannot be empty.", 400
    if not name or not email:
        return "Name and email are required.", 400

    # Add the message to the PostgreSQL database using our new DAL function
    message_id = messages_dal.add_message(name, email, message_text)

    if message_id:
        # Render a success page
        return render_template('EncouragementPage.html')
    else:
        # Handle the case where the message could not be saved
        return "There was an error saving your message.", 500

@app.route('/messages')
@auth.login_required
def view_messages():
    """
    Admin-facing page to view all submitted messages.
    This route is protected by HTTP Basic Authentication.
    """
    # This needs a new DAL function, e.g., all_messages = messages_dal.get_all_messages()
    all_messages = [] # Placeholder
    return render_template('admin_view.html', messages=all_messages)

@app.route('/delete-message/<int:message_id>', methods=['POST'])
@auth.login_required
def delete_message(message_id):
    """
    Admin action to delete a specific message.
    """
    # This needs a new DAL function, e.g., messages_dal.delete_message(message_id)
    print(f"Request to delete message {message_id}") # Placeholder
    # Redirect back to the admin message view after deletion
    return redirect(url_for('view_messages'))

if __name__ == '__main__':
    # Initialize the database when the app starts
    app.run(debug=True) # Use debug mode for local development
