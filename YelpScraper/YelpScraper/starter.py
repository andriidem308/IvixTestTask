import importlib

from scrapy.crawler import CrawlerProcess


def process_exported_file(filename):
    with open(filename) as f:
        business_records = f.read().split('\n')
        business_records = [rec for rec in business_records if rec]

    with open(filename, 'w') as file_in:
        file_in.write('[')
        for record in business_records[:-1]:
            file_in.write(f'{record}, ')
        if business_records:
            file_in.write(business_records[-1])
        file_in.write(']')


spider_path = importlib.import_module(f'spiders.yelp_spider')
spider_class = 'YelpSpider'
category = 'Home Cleaners'
location = 'San Francisco, CA'

export_file_path = '/tmp/YelpSpiderExport.json'
open(export_file_path, 'w').close()  # clear file

process = CrawlerProcess({
    'FEED_URI': f'file://{export_file_path}',
})
process.crawl(
    crawler_or_spidercls=getattr(spider_path, spider_class),
    category=category,
    location=location
)
process.start()

process_exported_file(export_file_path)

