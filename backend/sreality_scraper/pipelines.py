import os

import psycopg2
from urllib.parse import urlparse
from itemadapter import ItemAdapter

class SrealityScraperPipeline:
    DB_URI = os.getenv("API_DB_CONNECTION_STRING")

    INSERT_ITEM_QUERY = """
        INSERT INTO flat_ads (title, image) VALUES ($1, $2)
    """

    def __init__(self):
        # Extract connection parameters from the DB URI
        self.params = urlparse(self.DB_URI)
        self.pg_connection_dict = {
            'dbname': params.hostname,
            'user': params.username,
            'password': params.password,
            'port': params.port,
            'host': params.scheme
        }
        # Create a connection and a cursor
        self.conn = None
        self.cursor = None

    def open_spider(self, spider):
        self.conn = psycopg2.connect(**self.pg_connection_dict)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if isinstance(str, adapter.get('title')) and isinstance(str, adapter.get('image')):
            self.conn.execute(self.INSERT_ITEM_QUERY, (adapter.get('title'), adapter.get('image')))
        else:
            raise ValueError('Invalid item data')
        return item