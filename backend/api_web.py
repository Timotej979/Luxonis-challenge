import os
import logging
import json

# DB imports
import psycopg2
from flask_sqlalchemy import SQLAlchemy

# Flask imports
from flask import Flask, request

# Subprocess imports
import subprocess

# Scraper imports
from scrapy.crawler import Crawler
from twisted.internet import reactor
from billiard import Process
from scrapy.utils.project import get_project_settings
from scrapy import signals
from sreality_scraper.spiders.flat_spider import FlatAdSpider


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("API_URL_PREFIX")
DB_URI = str(os.getenv("API_DB_CONNECTION_STRING"))

# Gloabl variables to store the Flask app and the DB connection pool
app = Flask('SrealityScraperAPI')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create the DB model
class Flats(db.Model):
    __tablename__ = "flat_ads"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    image = db.Column(db.String(255))

# Define the API routes
@app.route(f"{URL_PREFIX}/start-scraper", methods=["POST"])
def start_scraper():
    try:
        data = json.loads(request.data)
        item_count = data.get("item_count")
        subprocess.run(["scrapy", "crawl", "flat_ad_spider", "-a", f"item_count={item_count}"])
        return json.dumps({"status": "success"}), 200
    except Exception as e:
        log.error(f"Error starting the scraper: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}), 500

@app.route(f"{URL_PREFIX}/flat-items", methods=["GET"])
def get_flats():
    try:
        flats = Flats.query.all()
        return json.dumps([{"title": flat.title, "image": flat.image} for flat in flats]), 200
    except Exception as e:
        log.error(f"Error getting flats: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}), 500

@app.route(f"{URL_PREFIX}/clear-flats", methods=["DELETE"])
def clear_flats():
    try:
        Flats.query.delete()
        db.session.commit()
        return json.dumps({"status": "success"}), 200
    except Exception as e:
        log.error(f"Error clearing flats: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    # Depending on the config set prod or dev mode
    if APP_CONFIG == "prod":
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        DB_MAX_CONNECTIONS = 10
        DB_POOL_RECYCLE = 3600
        DB_MAX_OVERFLOW = 0
        DB_POOL_TIMEOUT = 60
        log = logging.getLogger()
        log.info("Running in development config")

    elif APP_CONFIG == "dev":
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Running in production config")

    else:
        raise ValueError("APP_CONFIG environment variable must be either 'prod' or 'dev'")
        os.exit(1)

    with app.app_context():
        # Create the DB tables
        db.create_all()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)