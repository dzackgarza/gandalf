import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)
app.config['PUBLIC_DIR'] = 'public'  # Configure the directory for static files


@app.route('/')
def index():
    return "Welcome to the Static File Server!"


@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(app.config['PUBLIC_DIR'], filename)
    except FileNotFoundError:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return "404 Not Found", 404


if __name__ == '__main__':
    # Create 'public' directory if it doesn't exist
    os.makedirs(app.config['PUBLIC_DIR'], exist_ok=True)
    #Add a test file
    with open(os.path.join(app.config['PUBLIC_DIR'], 'test.txt'), 'w') as f:
        f.write("This is a test file.")
    app.run(debug=True)
