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
            item['scpId'] = row.xpath("./a/text()").extract()
            item['href'] = row.xpath("./a/@href").extract()
            item['name'] = row.xpath("./text()").extract()[0][3:]
            # ^^^ indexing and list slice drops the preceding " - " ^^^
            items.append(item)
        return items