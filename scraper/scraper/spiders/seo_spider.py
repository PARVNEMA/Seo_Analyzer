import scrapy
from bs4 import BeautifulSoup

class SeoSpider(scrapy.Spider):
    name = "seo"
    
    def __init__(self, url=None, *args, **kwargs):
        super(SeoSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        # 1. Title
        title = response.css('title::text').get()
        if title:
            title = title.strip()
            
        # 2. Meta description
        meta_description = response.xpath("//meta[@name='description']/@content").get()
        if meta_description:
            meta_description = meta_description.strip()
            
        # 3. Headers
        headers = {}
        for h in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            extracted = response.css(f'{h}::text').getall()
            if extracted:
                headers[h] = [text.strip() for text in extracted if text.strip()]
                
        # 4. Images & Alt text
        images = response.css('img')
        total_images = len(images)
        missing_alt = sum(1 for img in images if not img.attrib.get('alt'))
        
        # 5. Links
        links = response.css('a::attr(href)').getall()
        total_links = len(links)
        
        # We were instructed to skip HTTP status checking for speed in Phase 1
        broken_links = 0  # Placeholder, skipping actual HTTP HEAD requests
        
        # 6. Raw Text Content (using BeautifulSoup for cleaner extraction)
        soup = BeautifulSoup(response.body, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            script.decompose()
            
        text_content = soup.get_text(separator=' ')
        # Clean up whitespace
        text_content = ' '.join(text_content.split())
        
        yield {
            'url': response.url,
            'title': title,
            'meta_description': meta_description,
            'headers': headers,
            'total_images': total_images,
            'missing_alt_images': missing_alt,
            'total_links': total_links,
            'broken_links': broken_links,
            'text_content': text_content
        }
