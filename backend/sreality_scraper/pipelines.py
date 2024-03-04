import os
import logging
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
from itemadapter import ItemAdapter

class SrealityScraperPipeline:
    DB_URI = os.getenv("API_DB_CONNECTION_STRING")

    INSERT_QUERY = sql.SQL(
        "INSERT INTO flat_ads (title, image) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    )

    def __init__(self):
        # Extract connection parameters from the DB URI
        self.params = urlparse(self.DB_URI)
        self.pg_connection_dict = {
            'dbname': self.params.path[1:],
            'user': self.params.username,
            'password': self.params.password,
            'port': self.params.port,
            'host': self.params.hostname
        }
        # Create a connection and a cursor
        self.conn = None
        self.cursor = None

    def open_spider(self, spider):
        # Connect to the DB and get the cursor
        self.conn = psycopg2.connect(**self.pg_connection_dict)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Extract the title and image from the item
        title = adapter.get('title')
        image = adapter.get('image')
        # Check if the item is valid
        if isinstance(title, str) and isinstance(image, str):
            # Insert the item into the DB
            self.cursor.execute(self.INSERT_QUERY, (title, image))
        else:
            logging.error(f"Invalid item: {item}")
        return item