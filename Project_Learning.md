# Project Learnings

## How does spider is following links

   ` rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )`

* CrawlSpider Inheritance (Line 7): The SiteSpider class inherits from CrawlSpider instead of the standard scrapy.Spider. CrawlSpider provides a mechanism for following links by defining a set of rules.

* LinkExtractor(): This extracts all the <a> links (HTML anchor tags) from the page. Since it's instantiated without arguments here, it targets all hyperlinks. However, Scrapy automatically filters them based on the `self.allowed_domains` property defined in __init__ (lines 20–23), which restricts the crawler from leaving the starting website.

* callback='parse_item': For every extracted link that is followed and successfully downloaded, Scrapy forwards its response to the
parse_item
 method to extract details like title, meta description, and image alt tags.

* `follow=True`: This is the parameter that triggers recursion. When set to True, it tells Scrapy to extract and follow new links found on the newly crawled pages as well, repeating the process indefinitely until no new unique links within the allowed_domains are found.


## how Data is being saved in supabase backend

* in crawler there is a pipeline file which is used to data postprocessing so in that pipeline we call `process_item`

* in `process_item` we call ws post method '@router.post("/webhook/crawls/{job_id}")' webhook to store that data to superbase


### SEO Analysis of website (only one page)

* so in seo analysis we are not storing anything in the database we are just computing and showing it to user
'/analyze' analyze the seo
'/analyze-graph' analyze the seo using langgraph workflow

* analyze-graph uses langgraph

crawler node -> technical_audit_node -> on_page_audit_node -> intent_classifier_node -> competitor_scraper_node -> report_generator_node

this is the flow of nodes and in any case if error occurs directly report_generator_node will be called and currently we are using inmemorysaver
