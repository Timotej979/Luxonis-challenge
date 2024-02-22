import scrapy
import asyncio
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class FlatAdSpider(scrapy.Spider):
    name = 'flat_ad_spider'
    flats_on_sale_url = 'https://www.sreality.cz/hledani/prodej/byty'

    def parse():

        