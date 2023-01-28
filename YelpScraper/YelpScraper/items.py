import scrapy


class Business(scrapy.Item):
    Name = scrapy.Field()
    Rating = scrapy.Field()
    ReviewsNumber = scrapy.Field()
    URL = scrapy.Field()
    Website = scrapy.Field()
    Reviews = scrapy.Field()


class Review(scrapy.Item):
    ReviewerName = scrapy.Field()
    Location = scrapy.Field()
    Date = scrapy.Field()

