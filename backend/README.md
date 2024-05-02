# Scraper API

Scraper API is a RESTful API that scrapes data from the [https://www.sreality.cz/](https://www.sreality.cz/) website and saves it to the database. The API is built using the Flask framework and the Scrapy framework using a pipeline with psycopg2 native driver to directly write scraped data to the DB. The API is served through the NGINX reverse proxy.

The API has three available methods on its custom endpoint:
- - **POST request: /scraper-api/v1/start-scraper** - Starts the scraper and saves the data to the database.
```bash
curl --request POST --header "Content-Type: application/json" --data '{"item_count": 600}' http://127.0.0.1:8080/scraper-api/v1/start-scraper
```
- **GET request: /scraper-api/v1/flat-items** - Returns all the scraped items from the database.
```bash
curl --request GET --header "Content-Type: application/json" http://127.0.0.1:8080/scraper-api/v1/flat-items
``` 
- **DELETE request: /scraper-api/v1/clear-flats** - Deletes all the scraped items from the database.
```bash
curl --request DELETE --header "Content-Type: application/json" http://127.0.0.1:8080/scraper-api/v1/clear-flats
```