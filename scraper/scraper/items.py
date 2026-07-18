# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from urllib import response
import scrapy

# @dataclass
class ScraperItem(scrapy.Item):
            url=scrapy.Field(),
            title=scrapy.Field(),
            meta_description=scrapy.Field(),
            headers=scrapy.Field(),
            total_images=scrapy.Field(),
            missing_alt_images=scrapy.Field(),
            total_links=scrapy.Field(),
            broken_links=scrapy.Field(),
            text_content=scrapy.Field()
