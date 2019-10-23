from scrapy.spiders import Spider

class KoreanSpider(Spider):
    name = 's1'
    allowed_domains = ['scp-int.wikidot.com']
    start_urls = [ "http://scp-int.wikidot.com/ko-hub" ]

    def parse(self, response):
        rows = response.xpath("//div[@class='content-panel standalone series'][1]/ul[2]/li")
        items = []
        for row in rows:
            item = {}
            #item['line'] = row.xpath(".").extract()
            item['scpId'] = row.xpath("./a/text()").extract()
#             item['category'] = row.xpath("./h4/a/text()").extract()
#             item['appstore_link_url'] = row.xpath("a[1]/@href")[0].extract()
#             item['img_src_url'] = row.xpath("./a/img/@src").extract()
            items.append(item)
        return items