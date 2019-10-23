from scrapy.spiders import Spider
from scrapy import Request

class KoreanSpider(Spider):
    name = 'koreanSpider'
    allowed_domains = ['scp-int.wikidot.com']
    start_urls = [ "http://scp-int.wikidot.com/ko-hub" ]
    #englishBaseUrl = "http://scp-int.wikidot.com"
    
    # vvv this is very important because we are scraping multiple pages and don't want to get in trouble
    custom_settings = { 'DOWNLOAD_DELAY' : 0.5 }
    # ^^^ inlude this line to wait 0.5 seconds between each download ^^^

    def parse(self, response):
        rows = response.xpath("//div[@class='content-panel standalone series'][1]/ul[2]/li")
        rows = rows[:2] # limit rows when testing to save time
        items = []
        for row in rows:
            # the data to save
            item = {}
            
            # parse stuff on this page
            item['scpId'] = row.xpath("./a/text()").extract()
            item['href'] = row.xpath("./a/@href").extract()[0] # indexing at 0 appears to get the string
            item['name'] = row.xpath("./text()").extract()[0][3:]
            # ^^^ indexing and list slice drops the preceding " - " ^^^
            
            # parse stuff on the linked page
            request = Request("http://scp-int.wikidot.com" + item['href'], callback=self.parseEnglish) # get linked page and parse it with helper
            request.meta['data'] = item # spooky stuff for communicating between this and helper
            
            # save the data returned from helper (which includes the original scraped data)
            items.append(request)
            
        return items
    
    def parseEnglish(self, response):
        item = response.meta['data'] # tricky line does wierd stuff to let you communicate with parse
        item['englishRating'] = response.xpath("//span[@class='number prw54353']")
        return item
        