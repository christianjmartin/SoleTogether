from flask import Flask, render_template, request, redirect, url_for, jsonify, session

# python3 -m venv path/to/venv
# source path/to/venv/bin/activate
# python3 -m pip install flask

app = Flask(__name__)
app.secret_key = 'QEWOJFE3FIOENVWIOVCEI'


@app.route('/')
def index():
    session.clear()
    # Render the home page template
    return render_template('index.html')

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    return render_template(('homepage.html'))


if __name__ == '__main__':
    app.run(debug=True)