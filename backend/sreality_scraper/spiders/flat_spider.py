import os
import json

import scrapy
from scrapy.exceptions import CloseSpider

class FlatAdSpider(scrapy.Spider):
    name = 'flat_ad_spider'
    flats_loaded = 0
    flats_to_load = 500
    start_urls = [
            f'https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&per_page={flats_to_load}&tms=1687358646532'
        ]

    def __init__(self, item_count=None,**kwargs):
        if isinstance(item_count, int):
            self.flats_to_load = item_count

    def parse(self, response, **kwargs):
        res_data = json.loads(response.text)
        for flat in res_data["_embedded"]["estates"]:
            yield {
                'title': flat["name"],
                'image': flat["_links"]["images"][0]["href"],
            }
        self.flats_loaded +=1
        if self.flats_loaded >= self.flats_to_load:
            self.log('Closing the spider.')
            raise CloseSpider(f'Scraping finished, required number of flats: {self.flats_to_load} scraped.')