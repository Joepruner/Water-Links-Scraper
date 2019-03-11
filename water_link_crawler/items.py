# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WaterLink(scrapy.Item):
    previous_url = scrapy.Field()
    current_root = scrapy.Field()
    current_page = scrpay.Field()
    match_count = scrapy.Field()
    quality = scrapy.Field()
    high_quality = scrapy.Field()
    high_quality_scope = scrapy.Field()
    matched_href = scrapy.Field()
    matched_keywords = scrapy.Field()
    found_in = scrapy.Field()
    hops_from_start_root = scrapy.Field()
    next_url = scrapy.Field()
