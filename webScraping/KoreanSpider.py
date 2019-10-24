from scrapy.spiders import Spider
from scrapy import Request

class KoreanSpider(Spider):
    name = 'koreanSpider'
    allowed_domains = ['scp-int.wikidot.com', 'ko.scp-wiki.net'] # don't forget to update this
    start_urls = [ "http://scp-int.wikidot.com/ko-hub" ]
    
    englishDocumentsFolder = "englishFromKorean/"
    koreanDocumentsFolder = "koreanOriginals/"
    englishBaseUrl = "http://scp-int.wikidot.com"
    koreanBaseUrl = "http://ko.scp-wiki.net"
    
    # vvv this is very important because we are scraping multiple pages and don't want to get in trouble
    custom_settings = { 'DOWNLOAD_DELAY' : 0.5 }
    # ^^^ inlude this line to wait 0.5 seconds between each download ^^^

    def parse(self, response):
        rows = response.xpath("//div[@class='content-panel standalone series'][1]/ul[2]/li")
        #rows = rows[3:5] # limit rows when testing to save time
        items = []
        for row in rows:
            # the data to save
            item = {}
            
            # parse stuff on this page
            item['scpId'] = row.xpath("./a/text()").extract()[0] # indexing at 0 appears to get the string
            item['href'] = row.xpath("./a/@href").extract()[0]
            item['name'] = row.xpath("./text()").extract()[0][3:] # list slice drops the preceding " - "
            
            # parse stuff on the linked pages
            request = Request(self.englishBaseUrl + item['href'], callback=self.parseNextPages) # get linked page and parse it with helper
            request.meta['data'] = item # spooky stuff for communicating between this and helper
            
            # save the data returned from helper (which includes the original scraped data)
            items.append(request)
            
        return items
    
    def parseNextPages(self, response):
        item = response.meta['data'] # tricky line does wierd stuff to let you communicate with parse
        
        # same sort of thing as before
        item['englishRating'] = response.xpath("//span[@class='rate-points']/span/text()").extract()
        
        # save the english version to a file - maybe a bit hacky
        f = open(self.englishDocumentsFolder + item["scpId"] + ".html", "w") # w for write - overwrites all file content
        f.write(response.text)
        f.close()
        
        # and save just the text for simplicity
        f = open(self.englishDocumentsFolder + item["scpId"] + ".txt", "w")
        for paragraph in response.xpath("//div[@id='page-content']//text()"):
            f.write(paragraph.extract())
        f.close
        
        # now get the Korean
        # I don't know why this has to be done from this function, but it called a "hackathon" for a reason, right?
        request = Request(self.koreanBaseUrl + item['href'], callback=self.parseFinalPage)
        request.meta['data'] = item
        
        # we did it :)
        return request
    
    def parseFinalPage(self, response):
        item = response.meta['data']
        
        item['koreanRating'] = response.xpath("//span[@class='rate-points']/span/text()").extract()
        
        # html
        f = open(self.koreanDocumentsFolder + item["scpId"] + ".html", "w")
        f.write(response.text)
        f.close()
        
        # txt
        f = open(self.koreanDocumentsFolder + item["scpId"] + ".txt", "w")
        for paragraph in response.xpath("//div[@id='page-content']//text()"):
            f.write(paragraph.extract())
        f.close
        
        # we did it :)
        return item
        