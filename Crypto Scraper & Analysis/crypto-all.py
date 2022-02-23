# run with
# scrapy runspider a3-emehrotr-crypto-3.py -o -:csv > 3.csv 2> TRACE
# Author: Eshan Mehrotra
# Andrew ID: emehrotr


from gzip import READ
from scrapy import Request
from scrapy.spiders import Spider

class CryptoSpider(Spider): 
    name = "crypto" 
    handle_httpstatus_list = [404, 403] 
    allowed_domains = ['coinmarketcap.com']
    baseurl = 'https://coinmarketcap.com' 
    start_urls = [baseurl]
    
    custom_settings = { 
    'DOWNLOAD_DELAY': 0.5, 
    'DOWNLOADER_CLIENT_TLS_METHOD' : 'TLSv1.2', 
    'USER_AGENT' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36' 
    }
    
    def parse(self, response): 
        '''
        Parses the response we get from the website to find the Name, Price and Link of the Top N Cryptocurrencies 
        on the page.
        Return the list with each crypto as an item to be written to the CSV by Scrapy
        and creates another request with the link of each crypto and the corresponding callback function to scrape 
        each page
        '''
        rows = response.xpath('//table/tbody/tr') 
        ans=[] 
        for row in rows:
            item = {}
            item['Name'] = row.xpath('./td[3]//text()').getall()[0]
            item['Price'] = "".join(row.xpath('./td[4]//span/text()').getall())
            coin_url = item['Link'] = row.xpath('./td[3]//a/@href').get()
            req = Request(self.baseurl+coin_url,callback=self.parse_2)
            req.meta['x'] = item
            ans.append(req)
        return ans

    def parse_2(self, response):
        '''
        Parses the response we get each crypto link to find the details about the cryptocurrency. 
        Returns an item with all relevant details of the cryptocurrency to be written to the CSV by Scrapy
        '''
        item = response.meta['x']
        # Pickup Price again if earlier Price was read as 0 from Main Page Table due to JavaScript returning a very small decimal value
        if (item['Price'] == "$0.00"):
            item['Price'] = response.xpath('//div[@class="priceValue smallerPrice"]//text()').extract()

        item['Market Cap'] = response.xpath('//tr[th/text()="Market Cap"]/td/span/text()').extract()[0]
        item['Circulating Supply'] = response.xpath('//tr[th/text()="Circulating Supply"]/td/text()').extract()[0]
        item['Total Supply'] = response.xpath('//tr[th/text()="Total Supply"]/td/text()').extract()[0]
        item['Max Supply'] = response.xpath('//tr[th/text()="Max Supply"]/td/text()').extract()[0]
        item['All Time High Value'] = response.xpath('//tr[th/div/text()="All Time High"]/td//text()').extract()[0]
        item['All Time High Date'] = response.xpath('//tr/th[div/text()="All Time High"]/small/text()').extract()[0]
        item['All Time Low Value'] = response.xpath('//tr[th/div/text()="All Time Low"]/td//text()').extract()[0]
        item['All Time Low Date'] = response.xpath('//tr/th[div/text()="All Time Low"]/small/text()').extract()[0]
        return item