import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup

from scraper.items import ScraperItem

class SiteSeoSpider(CrawlSpider):
    name = "site_seo_spider"

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def __init__(self, start_url=None, job_id=None, *args, **kwargs):
        super(SiteSeoSpider, self).__init__(*args, **kwargs)
        self.job_id = job_id
        if start_url:
            self.start_urls = [start_url]
            from urllib.parse import urlparse
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]
        else:
            self.start_urls = []

    def parse_item(self, response):

        item=ScraperItem()
        # 1. Title
        title = response.css('title::text').get()
        if title:
            title = title.strip()
        item['title'] = title

        # 2. Meta description
        meta_description = response.xpath("//meta[@name='description']/@content").get()
        if meta_description:
            meta_description = meta_description.strip()

        item['meta_description'] = meta_description
        # 3. Headers
        headers = {}
        for h in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            extracted = response.css(f'{h}::text').getall()
            if extracted:
                headers[h] = [text.strip() for text in extracted if text.strip()]

        item['headers'] = headers
        # 4. Images & Alt text
        images = response.css('img')
        total_images = len(images)
        item['total_images'] = total_images
        missing_alt = sum(1 for img in images if not img.attrib.get('alt'))

        item['missing_alt_images'] = missing_alt
        # 5. Links
        links = response.css('a::attr(href)').getall()
        total_links = len(links)
        broken_links = 0
        item['total_links'] = total_links
        item['broken_links'] = broken_links

        # 6. Raw Text Content
        soup = BeautifulSoup(response.body, 'html.parser')
        for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script.decompose()
        text_content = ' '.join(soup.get_text(separator=' ').split())

        item['text_content'] = text_content

        yield item

