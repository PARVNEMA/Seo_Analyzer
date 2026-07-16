import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup


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

        meta_description = response.xpath("//meta[@name='description']/@content").get()
        if meta_description:
            meta_description = meta_description.strip()

        images = response.css('img')
        total_images = len(images)
        missing_alt = sum(1 for img in images if not img.attrib.get('alt'))

        links = response.css('a::attr(href)').getall()
        total_links = len(links)
        broken_links = 0

        soup = BeautifulSoup(response.body, 'html.parser')
        for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script.decompose()
        text_content = ' '.join(soup.get_text(separator=' ').split())

        yield {
            'url': response.url,
            'title': title,
            'meta_description': meta_description,
            'headers': {},
            'total_images': total_images,
            'missing_alt_images': missing_alt,
            'total_links': total_links,
            'broken_links': broken_links,
            'text_content': text_content
        }
