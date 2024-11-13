from flask import Flask, render_template, request, redirect, url_for
from functools import wraps
import subprocess
import os

app = Flask(__name__)

# Configuration for basic authentication
USERNAME = 'VBCG'
PASSWORD = 'i-robot'

# Path to the user_input.txt file
USER_INPUT_FILE = '/home/ubuntu/abtests/testnov6/default_user/user_input.txt'  # Update this path as needed

# Basic authentication decorator
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return app.response_class(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET', 'POST'])
@requires_auth
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input:
            try:
                # Save the user input to user_input.txt
                with open(USER_INPUT_FILE, 'w') as f:
                    f.write(user_input)
                
                # Execute controller.py
                result = subprocess.run(
                    ['python', '/home/ubuntu/abtests/testnov6/controller.py'],
                    capture_output=True, text=True
                )
                output = result.stdout
                error = result.stderr
                return render_template('result.html', output=output, error=error)
            except Exception as e:
                return render_template('result.html', output='', error=str(e))
        else:
            error = 'Please enter text before submitting.'
            return render_template('index.html', error=error)
    return render_template('index.html', error='')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
