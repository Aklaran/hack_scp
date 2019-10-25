from scrapy.spiders import Spider
from scrapy import Request, FormRequest, Selector
import re
import json

class KoreanSpider(Spider):
    name = 'koreanSpider'
    allowed_domains = ['scp-int.wikidot.com', 'ko.scp-wiki.net', 'www.wikidot.com'] # don't forget to update this
    start_urls = [ "http://scp-int.wikidot.com/ko-hub" ]
    
    englishDocumentsFolder = "englishFromKorean/"
    koreanDocumentsFolder = "koreanOriginals/"
    englishBaseUrl = "http://scp-int.wikidot.com"
    koreanBaseUrl = "http://ko.scp-wiki.net"
    englishToken = '610da9ba2f8fa1ca5ef14c7488cdfc16'
    koreanToken = 'd6be53a2948f8f5eb10d764ecc24c198'
    
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
            
            # parse stuff on the linked pages
            request = Request(self.englishBaseUrl + item['href'], callback=self.parseEnglishPage) # get linked page and parse it with helper
            request.meta['data'] = item # spooky stuff for communicating between this and helper
            
            # save the data returned from helper (which includes the original scraped data)
            items.append(request)
            
        return items
    
    def parseEnglishPage(self, response):
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

        # grab the pageId from a script tag
        # we'll need this to open the revision history tab
        pageScripts = response.xpath("/html/head/script").extract()
        pageId = ''
        for script in pageScripts:
            pageId_search = re.search('WIKIREQUEST\.info\.pageId = (.*);', script)
            if pageId_search:
                pageId = pageId_search.group(1)

        # open revision history tab and get the initial author + date
        # important that you have wikidot_token7 in both the formdata and the cookie!
        request = FormRequest(self.englishBaseUrl + '/ajax-module-connector.php', 
                                callback=self.parseEnglishAuthorAndDate,
                                method='POST', 
                                formdata={'page_id': pageId, 'moduleName': 'history/PageRevisionListModule', 'wikidot_token7': self.englishToken, 'page': '1', 'perpage': '20'},
                                cookies={"wikidot_token7": self.englishToken})
        request.meta['data'] = item

        return request

    def parseEnglishAuthorAndDate(self, response):
        item = response.meta['data']

        # parse JSON because this was called with a AJAX request
        data = json.loads(response.body)

        self.logger.info("parsing english author and date")

        # make a selector from the inner html so we can run xpaths on it
        selector = Selector(text=data['body'], type='html')

        # select the oldest item in the revision table
        initialRevision = selector.xpath('//table[@class="page-history"]/tr[last()]')

        item['englishDate'] = initialRevision.xpath('td[6]/span/text()').extract_first()
        item['englishAuthor'] = initialRevision.xpath('td[5]/span/a[2]/text()').extract_first()

        # now move to the english author page to get their karma
        authorUrl = initialRevision.xpath('td[5]/span/a[2]/@href').extract_first()
        request = Request(authorUrl, callback=self.parseEnglishAuthorPage)
        request.meta['data'] = item

        return request
    
    def parseEnglishAuthorPage(self, response):
        item = response.meta['data']

        # [0] gets the string and strip gets rid of whitespace
        item['englishAuthorKarma'] = response.xpath('//*[@id="user-info-area"]/div/dl/dd[3]/text()[1]').extract()[0].strip()

        # now get the Korean
        # I don't know why this has to be done from this function, but it called a "hackathon" for a reason, right?
        request = Request(self.koreanBaseUrl + item['href'], callback=self.parseKoreanPage)
        request.meta['data'] = item

        return request
    
    def parseKoreanPage(self, response):
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

        # grab the pageId from a script tag
        # we'll need this to open the revision history tab
        pageScripts = response.xpath("/html/head/script").extract()
        pageId = ''
        for script in pageScripts:
            pageId_search = re.search('WIKIREQUEST\.info\.pageId = (.*);', script)
            if pageId_search:
                pageId = pageId_search.group(1)

        self.logger.info('pageId: %s', pageId)

        # open revision history tab and get the initial author + date
        # important that you have wikidot_token7 in both the formdata and the cookie!
        request = FormRequest(self.koreanBaseUrl + '/ajax-module-connector.php', 
                                callback=self.parseKoreanAuthorAndDate,
                                method='POST', 
                                formdata={'page_id': pageId, 'moduleName': 'history/PageRevisionListModule', 'wikidot_token7': self.koreanToken, 'page': '1', 'perpage': '20'},
                                cookies={"wikidot_token7": self.koreanToken})
        request.meta['data'] = item

        return request
    
    def parseKoreanAuthorAndDate(self, response):
        item = response.meta['data']

        # parse JSON because this was called with a AJAX request
        data = json.loads(response.body)

        # make a selector from the inner html so we can run xpaths on it
        selector = Selector(text=data['body'], type='html')

        # select the oldest item in the revision table
        initialRevision = selector.xpath('//table[@class="page-history"]/tr[last()]')

        item['koreanDate'] = initialRevision.xpath('td[6]/span/text()').extract_first()
        item['koreanAuthor'] = initialRevision.xpath('td[5]/span/a[2]/text()').extract_first()

        # now move to the korean author page to get their karma
        authorUrl = initialRevision.xpath('td[5]/span/a[2]/@href').extract_first()
        request = Request(authorUrl, callback=self.parseKoreanAuthorPage)
        request.meta['data'] = item

        return request

    def parseKoreanAuthorPage(self, response):
        item = response.meta['data']

        # [0] gets the string and strip gets rid of whitespace
        item['koreanAuthorKarma'] = response.xpath('//*[@id="user-info-area"]/div/dl/dd[3]/text()[1]').extract()[0].strip()

        # that's all folks
        return item