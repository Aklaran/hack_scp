# Run with
#
# scrapy runspider simple-scraper.py –t csv –o out-1.csv


# A very bare minimum spider

from scrapy.spiders import Spider

class MySpider(Spider):
    name = 's0'
    allowed_domains = ['craigslist.org']
    start_urls = [ "https://pittsburgh.craigslist.org/search/apa" ]
    
    def parse(self, response):
        rows = response.xpath("//p[@class='result-info']")
        items = []
        for row in rows:
            item = {}
            item['title'] = row.xpath("./a/text()").extract()
            item['location'] = row.xpath(".//span[@class='result-meta']/span[@class='result-hood']/text()").extract()
            item['price'] = row.xpath(".//span[@class='result-price']/text()").extract()
            item['size'] = row.xpath(".//span[@class='result-meta']/span[@class='housing']/text()").extract()
            items.append(item)
        return items
        
        
        
