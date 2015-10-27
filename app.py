from flask import Flask, url_for, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = '/scraper/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
