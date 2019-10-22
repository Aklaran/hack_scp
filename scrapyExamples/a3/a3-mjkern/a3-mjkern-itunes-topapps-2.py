# mjkern - a3
# modified from the first version to scrape multiple pages

# Run with
# scrapy runspider simple-scraper.py –t csv –o out-1.csv


from scrapy.spiders import Spider
from scrapy import Request

class MySpider(Spider):
    name = 's1'
    allowed_domains = [ 'apple.com' ]
    start_urls = [ "https://www.apple.com/itunes/charts/free-apps/" ]
    custom_settings = { 'DOWNLOAD_DELAY' : 0.5 }

    def parse(self, response):
        rows = response.xpath("//div/section/div/ul/li")
        items = []
        for row in rows: # remove limit later
            item = {}
            item['app_name'] = row.xpath("./h3/a/text()").extract()
            item['category'] = row.xpath("./h4/a/text()").extract()
            #item['appstore_link_url'] = row.xpath("./h4/a/@href").extract()
            item['appstore_link_url'] = row.xpath("a[1]/@href")[0].extract()
            item['img_src_url'] = row.xpath("./a/img/@src").extract()
            req = Request(item['appstore_link_url'], callback=self.parse2)
            req.meta['data'] = item
            items.append(req)
        return items

    def parse2(self, response):
        item = response.meta['data']
        string = response.xpath("//figcaption[@class='we-rating-count star-rating__count']/text()").extract()[0]
        item['star_rating'], item['num_ratings'] = string.split(', ')
        return item

