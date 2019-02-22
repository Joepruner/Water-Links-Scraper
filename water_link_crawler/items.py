# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WaterLink(scrapy.Item):
    referer_url = scrapy.Field()
    match_url = scrapy.Field()
    relevent_text = scrapy.Field()
    found_in = scrapy.Field()


class WaterLinkGroup(scrapy.Item):
    referer_url = scrapy.Field()
    num_match_urls = scrapy.Field()
