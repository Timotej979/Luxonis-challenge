import logging, os, sys

import asyncio, asyncpg
import aiohttp_sqlalchemy as ahsa

from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine

# DB imports
# from db_abstraction.dal import DAL
from db_abstraction.db_model import metadata

# Scraper imports
from sreality_scraper.sreality_scraper.spiders.flat_spider import FlatAdSpider
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.reactor import install_reactor


# Get environment variables
APP_CONFIG = os.getenv("APP_CONFIG")
URL_PREFIX = os.getenv("API_URL_PREFIX")
DB_URI = str(os.getenv("API_DB_CONNECTION_STRING"))
DB_MAX_CONNECTIONS = int(os.getenv("API_DB_MAX_CONNECTIONS"))
DB_POOL_RECYCLE = int(os.getenv("API_DB_POOL_RECYCLE"))
DB_MAX_OVERFLOW = int(os.getenv("API_DB_MAX_OVERFLOW"))
DB_POOL_TIMEOUT = int(os.getenv("API_DB_POOL_TIMEOUT"))


#########################################################################
### API CLASS ###
class API_Server():
    """
    API_Server class controls the behaviour of API server
    """
    
    # Configure routes table and all available methods
    routes = web.RouteTableDef()

    # Healthcheck
    @routes.get('/healthz')
    async def health_check(request):
        log.info("Api test running\n")
        return web.Response(text="## API test successfull ##\n")


    ######################################################## API METHODS ###############################################################
    @routes.post('/startCrawler')
    async def start_crawler(request):
        log.info("POST staring the crawler\n")

        try:
            # Fetch the request data
            res_data = await request.json()
            item_count = res_data['item_count']

            # Check if the item_count is an integer
            if not isinstance(item_count, int):
                log.error("!! POST starting the crawler error: Item count is not an integer !!\n")
                return web.HTTPBadRequest("!! POST starting the crawler error: Item count is not an integer !!\n")

        except:
            log.exception("!! POST starting the crawler error: Couldn't fetch request data !!\n")
            return web.HTTPBadRequest("!! POST starting the crawler error: Couldn't fetch request data !!\n")
        else:
            # Set the number of flats to load
            log.info("POST starting the crawler: Item count set to: {}\n".format(item_count))
            kwargs = {'NUM_OF_FLATS': item_count}

            # Set up the crawler
            crawler_settings = Settings()
            crawler_settings.setmodule('sreality_scraper.sreality_scraper.settings')

            # Offload the crawler task to the event loop
            loop = asyncio.get_event_loop()

            # Pass custom argument to the spider using the kwargs parameter
            kwargs = {'item_count': item_count}
            crawler_runner = CrawlerRunner(crawler_settings)

            # Run the Twisted reactor in a separate thread
            await loop.run_in_executor(None, lambda: reactor.run(installSignalHandlers=0))

            # Run the crawl coroutine in the event loop
            await loop.run_in_executor(None, lambda: asyncio.run_coroutine_threadsafe(crawler_runner.crawl(FlatAdSpider, **kwargs), loop))

            return web.Response(text="## Crawler started ##\n")




    ############################################################################################################################################
    # Initialization for API app object
    async def initialize(self):
        log.info("API initialization started")
        self.subapp = web.Application()  

        log.info("Configuring API SQLAlchemy engine")
        self.subapp['engine'] = create_async_engine(DB_URI, 
                                                    echo = (False if APP_CONFIG == 'prod' else True),
                                                    connect_args={"server_settings": {"jit": "off"}},
                                                    pool_pre_ping=True, 
                                                    pool_size=DB_MAX_CONNECTIONS,
                                                    pool_recycle=DB_POOL_RECYCLE,
                                                    max_overflow=DB_MAX_OVERFLOW,
                                                    pool_timeout=DB_POOL_TIMEOUT)
        
        log.info("Binding SQLAlchemy engine to application object")
        ahsa.setup(self.subapp, [ahsa.bind(DB_URI)])

        log.info("Creating DB tables")
        await ahsa.init_db(self.subapp, metadata)

        log.info("Adding routes to application object")
        self.subapp.router.add_routes(self.routes)

        # Add sub-app to set the IP/sreality-api request
        self.app = web.Application()
        self.app.add_subapp(URL_PREFIX, self.subapp)

        log.info("API initialization complete")

    # Run API
    def start_server(self, host, port, loop):
        log.info("Server starting on address: http://{}:{}".format(host, port))
        web.run_app(self.app, host=host, port=port, loop=loop)


if __name__ == '__main__':
    # Set up operation mode for server
    if APP_CONFIG == 'dev':
        # Development build
        logging.basicConfig(level=logging.DEBUG)
        DB_MAX_CONNECTIONS = 10
        DB_POOL_RECYCLE = 3600
        DB_MAX_OVERFLOW = 0
        DB_POOL_TIMEOUT = 60
        log = logging.getLogger()
        log.info("Running in development config")

    elif APP_CONFIG == 'prod':
        # Production build
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Running in production config")

    else:
        # If APP_CONFIG env variable is not set abort start
        logging.basicConfig(level=logging.INFO)
        log = logging.getLogger()
        log.info("Environment variable APP_CONFIG is not set (Current value is: {}), please set it in  the environment file".format(APP_CONFIG))
        sys.exit(1)

    # Set up asyncio reactor for scrapy
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

    # Get asyncio loop
    loop = asyncio.get_event_loop()

    # Create WebServer object and initialize it
    server = API_Server()
    loop.run_until_complete(server.initialize())

    # Start the server
    server.start_server(host='0.0.0.0', port=5000, loop=loop)
    


