BOT_NAME = 'mca_scraper'

SPIDER_MODULES = ['mca_scraper.spiders']
NEWSPIDER_MODULE = 'mca_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure a delay for requests for the same website (default: 0)
# This is crucial for being a responsible scraper and avoiding bans.
DOWNLOAD_DELAY = 3

# Enable and configure the pipeline. The number (300) determines the order.
ITEM_PIPELINES = {
   'mca_scraper.pipelines.JsonWriterPipeline': 300,
}

# Set a custom User-Agent to identify our bot.
USER_AGENT = 'VerifiedJobMarketplaceBot/1.0 (+http://www.yourwebsite.com)'


# Enable our new pipeline and disable the old one
ITEM_PIPELINES = {
   # 'mca_scraper.pipelines.JsonWriterPipeline': 300, # Disable the old one
   'mca_scraper.pipelines.MongoPipeline': 300,      # Enable the new one
}

# Add your MongoDB connection settings
MONGO_URI = 'mongodb+srv://Scraper_use:2N49ArCe4RStECuU@marketplacecluster.yzch06m.mongodb.net/?retryWrites=true&w=majority&appName=MarketplaceCluster' 
MONGO_DATABASE = 'marketplace_data' # Name of the database to use
