from scrapy.spiders import Spider
from scrapy import Request

class KoreanSpider(Spider):
    name = 'koreanSpider'
    allowed_domains = ['scp-int.wikidot.com']
    start_urls = [ "http://scp-int.wikidot.com/ko-hub" ]
    englishDocumentsFolder = "englishFromKorean/"
    #englishBaseUrl = "http://scp-int.wikidot.com"
    
    # vvv this is very important because we are scraping multiple pages and don't want to get in trouble
    custom_settings = { 'DOWNLOAD_DELAY' : 0.5 }
    # ^^^ inlude this line to wait 0.5 seconds between each download ^^^

    def parse(self, response):
        rows = response.xpath("//div[@class='content-panel standalone series'][1]/ul[2]/li")
        rows = rows[3:5] # limit rows when testing to save time
        items = []
        for row in rows:
            # the data to save
            item = {}
            
            # parse stuff on this page
            item['scpId'] = row.xpath("./a/text()").extract()[0] # indexing at 0 appears to get the string
            item['href'] = row.xpath("./a/@href").extract()[0]
            item['name'] = row.xpath("./text()").extract()[0][3:] # list slice drops the preceding " - "
            
            # parse stuff on the linked page
            request = Request("http://scp-int.wikidot.com" + item['href'], callback=self.parseEnglish) # get linked page and parse it with helper
            request.meta['data'] = item # spooky stuff for communicating between this and helper
            
            # save the data returned from helper (which includes the original scraped data)
            items.append(request)
            
        return items
    
    def parseEnglish(self, response):
        item = response.meta['data'] # tricky line does wierd stuff to let you communicate with parse
        
        # same sort of thing as before
        item['englishRating'] = response.xpath("//span[@class='rate-points']/span/text()").extract()
        
        # write the text of the english version to a file - this is hacky!!!
        f = open(self.englishDocumentsFolder + item["scpId"] + ".html", "w") # a for append
        f.write(response.text) # making the choice to save the whole document - we can extract text later but better to have more than less
        f.close()
        
        # we did it :)
        return item
        