# mjkern - a3
# modified from simple scraper

# Run with
# scrapy runspider simple-scraper.py –t csv –o out-1.csv


from scrapy.spiders import Spider

class MySpider(Spider):
    name = 's0'
    allowed_domains = ['apple.com']
    start_urls = [ "https://www.apple.com/itunes/charts/free-apps/" ]

    def parse(self, response):
        rows = response.xpath("//div/section/div/ul/li")
        items = []
        for row in rows:
            item = {}
            item['app_name'] = row.xpath("./h3/a/text()").extract()
            item['category'] = row.xpath("./h4/a/text()").extract()
            item['appstore_link_url'] = row.xpath("a[1]/@href")[0].extract()
            item['img_src_url'] = row.xpath("./a/img/@src").extract()
            items.append(item)
        return items



