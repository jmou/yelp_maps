import os
import re
from datetime import datetime

import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor


class YelpBookmark(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip_code = scrapy.Field()
    phone = scrapy.Field()
    date_added = scrapy.Field()
    # biz_id = scrapy.Field()


class YelpBookmarksSpider(CrawlSpider):
    name = 'yelp_bookmarks'
    # allowed_domains = ['localhost']
    # start_urls = (
    #     'file://' + os.path.abspath('yelp.html'),
    # )
    allowed_domains = ['yelp.com']
    start_urls = (
        'http://www.yelp.com/user_details_bookmarks?userid=0cwT5wyOf5_qcxy94pf1rg',
    )
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//table[@class="fs_pagination_controls"]'), callback='parse_start_url'),
    )

    def parse_start_url(self, response):
        for row in response.css('.bookmark_row'):
            item = YelpBookmark()

            info = row.xpath('div[@class="book_biz_info"]')[0]
            item['name'] = info.xpath('h3/a/text()').extract()[0].strip()
            item['url'] = info.xpath('h3/a/@href').extract()[0]
            item['rating'] = info.xpath('div[@class="biz_rating"]/div/i/@title').re('([\d.]*) star rating')[0]
            item['review_count'] = info.xpath('div[@class="biz_rating"]/text()').re('(\d*) Reviews')[0]

            dirty_address = '\n'.join(info.xpath('address/text()').extract()).strip()
            address_lines = re.sub(r'\s*\n\s*', '\n', dirty_address).split('\n')
            if re.match(r'^\(\d{3}\) \d{3}-\d{4}$', address_lines[-1]):
                item['phone'] = address_lines.pop()
            match = re.match(r'([^,]*), (..) (\d{5})', address_lines[-1])
            if match:
                address_lines.pop()
                item['city'] = match.group(1)
                item['state'] = match.group(2)
                item['zip_code'] = match.group(3)
            if address_lines:
                item['address'] = address_lines[0]

            date_added = row.xpath('.//p[@class="book_biz_actions"]/text()').re('Added ([\d/]*)\\n')[0]
            item['date_added'] = datetime.strptime(date_added, '%m/%d/%Y').date().isoformat()
            # Only works when signed in
            # review_url = row.xpath('.//p[contains(@class, "write-review")]/a/@href')[0].extract()
            # item['biz_id'] = re.match(r'^https://www\.yelp\.com/writeareview/biz/([^?]*)\?', review_url).group(1)

            yield item
