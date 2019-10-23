from scrapy.spiders import Spider

class MySpider(Spider):
    name = 's1'
    allowed_domains = ['apple.com']
    start_urls = [ "https://www.apple.com/itunes/charts/free-apps/" ]

    def parse(self, response):
        rows = response.xpath("/html[@class='gr__scp-int_wikidot_com']/body[@id='html-body']/div[@id='skrollr-body']/div[@id='container-wrap-wrap']/div[@id='container-wrap']/div[@id='container']/div[@id='content-wrap']/div[@id='main-content']/div[@id='page-content']/table[@class='wiki-content-table']/tbody/tr")
        items = []
        for row in rows:
            item = {}
            item['author'] = row.xpath("./td[1]/span[@class='printuser avatarhover']/a/text()").extract()
#             item['category'] = row.xpath("./h4/a/text()").extract()
#             item['appstore_link_url'] = row.xpath("a[1]/@href")[0].extract()
#             item['img_src_url'] = row.xpath("./a/img/@src").extract()
            items.append(item)
        return items