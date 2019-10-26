from scrapy.spiders import Spider
from scrapy import Request, FormRequest, Selector
import re
import json

class ThaiSpider(Spider):
    name = 'thaiSpider'
    allowed_domains = ['scp-int.wikidot.com', 'www.wikidot.com', 'scp-th.wikidot.com'] # don't forget to update this
    start_urls = [ "http://scp-int.wikidot.com/th-hub" ]

    englishDocumentsFolder = "englishFromThai/"
    thaiDocumentsFolder = "thaiOriginals/"
    englishBaseUrl = "http://scp-int.wikidot.com"
    thaiBaseUrl = "http://scp-th.wikidot.com"
    englishToken = '610da9ba2f8fa1ca5ef14c7488cdfc16'
    thaiToken = 'd6be53a2948f8f5eb10d764ecc24c198'

    # vvv this is very important because we are scraping multiple pages and don't want to get in trouble
    custom_settings = { 'DOWNLOAD_DELAY' : 0.5,
                        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter' }
    # ^^^ inlude this line to wait 0.5 seconds between each download ^^^

    def parse(self, response):
        rows = response.xpath("//div[@id='page-content']/ul[1]/li")
#         rows = rows[3:5] # limit rows when testing to save time
        items = []
        for row in rows:
            # the data to save
            item = {}

            # parse stuff on this page
            if row.xpath("./text()").extract(): # check for annoying things
                item['scpId'] = row.xpath("./strong/a/text()").extract()[0] # indexing at 0 appears to get the string
                item['href'] = row.xpath("./strong/a/@href").extract()[0]
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

        # assuming the last item on the author info page is karma,
        # use regex to extract it
        karmaListItem = response.xpath('//*[@id="user-info-area"]/div/dl/dd').extract()[-1]
        karmaSearch = re.search("<dd>\s*(\w*\s*\w*)\s*<img", karmaListItem)
        if karmaSearch:
            karmaString = karmaSearch.group(1).strip()
        else:
            karmaString = 'Not found'

        item['englishAuthorKarma'] = karmaString

        # now get the Thai
        # I don't know why this has to be done from this function, but it called a "hackathon" for a reason, right?
        request = Request(self.thaiBaseUrl + item['href'], callback=self.parseThaiPage)
        request.meta['data'] = item

        return request

    def parseThaiPage(self, response):
        item = response.meta['data']

        item['thaiRating'] = response.xpath("//span[@class='rate-points']/span/text()").extract()

        # html
        f = open(self.thaiDocumentsFolder + item["scpId"] + ".html", "w")
        f.write(response.text)
        f.close()

        # txt
        f = open(self.thaiDocumentsFolder + item["scpId"] + ".txt", "w")
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
        request = FormRequest(self.thaiBaseUrl + '/ajax-module-connector.php',
                                callback=self.parseThaiAuthorAndDate,
                                method='POST',
                                formdata={'page_id': pageId, 'moduleName': 'history/PageRevisionListModule', 'wikidot_token7': self.thaiToken, 'page': '1', 'perpage': '20'},
                                cookies={"wikidot_token7": self.thaiToken})
        request.meta['data'] = item

        return request

    def parseThaiAuthorAndDate(self, response):
        item = response.meta['data']

        # parse JSON because this was called with a AJAX request
        data = json.loads(response.body)

        # make a selector from the inner html so we can run xpaths on it
        selector = Selector(text=data['body'], type='html')

        # select the oldest item in the revision table
        initialRevision = selector.xpath('//table[@class="page-history"]/tr[last()]')

        item['thaiDate'] = initialRevision.xpath('td[6]/span/text()').extract_first()
        item['thaiAuthor'] = initialRevision.xpath('td[5]/span/a[2]/text()').extract_first()

        # now move to the thai author page to get their karma
        authorUrl = initialRevision.xpath('td[5]/span/a[2]/@href').extract_first()
        request = Request(authorUrl, callback=self.parseThaiAuthorPage)
        request.meta['data'] = item

        return request

    def parseThaiAuthorPage(self, response):
        item = response.meta['data']

        # assuming the last item on the author info page is karma,
        # use regex to extract it
        karmaListItem = response.xpath('//*[@id="user-info-area"]/div/dl/dd').extract()[-1]
        karmaSearch = re.search("<dd>\s*(\w*\s*\w*)\s*<img", karmaListItem)
        if karmaSearch:
            karmaString = karmaSearch.group(1).strip()
        else:
            karmaString = 'Not found'

        item['thaiAuthorKarma'] = karmaString

        # that's all folks
        return item
