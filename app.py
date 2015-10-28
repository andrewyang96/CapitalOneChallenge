from flask import Flask, url_for, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scraper import scrape

from datetime import datetime

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

instagram_data = {}
def instagram_scrape():
    instagram_data = scrape(days=0.5)
scrape_job = scheduler.add_job(scrape, 'cron', minute=0)

# End database methods

@app.route('/')
def index(name=None):
    url_for('static', filename='static/style.css')
    url_for('static', filename='static/script.js')
    return render_template('index.html', name=name)

# Begin API methods

@app.route('/debug')
def debug(name=None):
    return jsonify(instagram_data)

# End API methods

if __name__ == "__main__":
    app.run()
