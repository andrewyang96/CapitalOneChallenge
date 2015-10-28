from flask import Flask, url_for, render_template

app = Flask(__name__)

# End database methods

@app.route('/')
def index(name=None):
    url_for('static', filename='static/style.css')
    url_for('static', filename='static/script.js')
    return render_template('index.html', name=name)

# Begin API methods

# TODO

# End API methods

if __name__ == "__main__":
    app.run()
