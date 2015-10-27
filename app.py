from flask import Flask, url_for, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/template')
def template(name=None):
    url_for('static', filename='static/style.css')
    url_for('static', filename='static/script.js')
    return render_template('index.html', name=name)

if __name__ == "__main__":
    app.run()
