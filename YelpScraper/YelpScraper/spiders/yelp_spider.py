import json
import re

import jmespath
import scrapy
from urllib.parse import unquote_plus

from YelpScraper.YelpScraper.items import Business, Review


class YelpSpider(scrapy.Spider):
    base_crawl_url = 'https://www.yelp.com/search?find_desc={}&find_loc={}&start=0'
    base_business_url = 'https://www.yelp.com{}&sort_by=date_asc'

    page_size = 10

    def __init__(self, category, location):
        self.category = category
        self.location = location

    def start_requests(self):
        yield scrapy.Request(url=self.base_crawl_url.format(self.category, self.location), callback=self.parse)

    def parse(self, response):
        links = set(response.xpath('//span[@class=" css-1egxyvc"]/a/@href').extract())
        for link in links:
            yield scrapy.Request(self.base_business_url.format(link), self.parse_business)

        if links:
            yield scrapy.Request(self.get_page(response.url), self.parse)

    def parse_business(self, response):
        script = response.xpath(
            '//script[@type="application/ld+json" and contains(text(), \'"@type":"LocalBusiness"\')]/text()'
        ).extract_first()
        business = json.loads(script)

        website_url_raw = response.xpath('//p[text()="Business website"]/../p/a/@href').extract_first()
        website_url_quoted = re.findall(r'url=(.*?)&', website_url_raw) if website_url_raw else ''
        website = unquote_plus(website_url_quoted[0]) if website_url_quoted else ''

        item = Business()
        item['Name'] = response.xpath('//h1/text()').extract_first()
        item['Rating'] = jmespath.search('aggregateRating.ratingValue', business) or 0
        item['ReviewsNumber'] = jmespath.search('aggregateRating.reviewCount', business) or 0
        item['URL'] = response.url.split('?')[0] if '?' in response.url else response.url
        item['Website'] = website
        item['Reviews'] = self.process_reviews(response)
        yield item

    def get_page(self, response_url):
        curr_offset = re.findall(r'start=(\d+)', response_url)[0]
        next_offset = int(curr_offset) + self.page_size
        next_page = re.sub(f'start={curr_offset}', f'start={next_offset}', response_url)
        return next_page

    @staticmethod
    def process_reviews(response):
        reviews = []
        raw_reviews = response.xpath('//div[contains(@class, "review_")]').extract()[:5]
        for raw_review in raw_reviews:
            review_selector = scrapy.Selector(text=raw_review)
            review = Review()
            review['ReviewerName'] = review_selector.xpath(
                '//a[@class="css-1m051bw" and contains(@href, "userid")]/text()').extract_first()
            review['Location'] = review_selector.xpath('//span[@class=" css-qgunke"]/text()').extract_first()
            review['Date'] = review_selector.xpath('//span[@class=" css-chan6m"]/text()').extract_first()
            reviews.append(review)
        return reviews
