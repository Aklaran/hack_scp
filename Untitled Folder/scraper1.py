from scrapy.spiders import Spider

class MySpider(Spider):
    name = 's1'
    allowed_domains = ['scp-int.wikidot.com']
    start_urls = [ "http://scp-int.wikidot.com/members-pages" ]

    def parse(self, response):
        rows = response.xpath("//table/tr")
        items = []
        for row in rows:
            item = {}
            #item['line'] = row.xpath(".").extract()
            item['author'] = row.xpath("./td[1]/span[@class='printuser avatarhover']/a/text()").extract()
#             item['category'] = row.xpath("./h4/a/text()").extract()
#             item['appstore_link_url'] = row.xpath("a[1]/@href")[0].extract()
#             item['img_src_url'] = row.xpath("./a/img/@src").extract()
            items.append(item)
        return items