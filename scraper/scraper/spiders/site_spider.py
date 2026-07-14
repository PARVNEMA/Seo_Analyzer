import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class SiteSpider(CrawlSpider):
    name = "site_spider"
    
    # We will use the start_url passed as argument
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def __init__(self, start_url=None, job_id=None, *args, **kwargs):
        super(SiteSpider, self).__init__(*args, **kwargs)
        self.job_id = job_id
        if start_url:
            self.start_urls = [start_url]
            # Restrict crawling to the domain of the start_url
            from urllib.parse import urlparse
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]
        else:
            self.start_urls = []

    def parse_item(self, response):
        title = response.css('title::text').get()
        if title:
            title = title.strip()
            
        yield {
            'url': response.url,
            'title': title,
            # Empty values for SEO metrics to maintain schema
            'meta_description': None,
            'headers': {},
            'total_images': 0,
            'missing_alt_images': 0,
            'total_links': 0,
            'broken_links': 0,
            'text_content': None
        }
