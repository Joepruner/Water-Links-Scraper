# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WaterLink(scrapy.Item):
    current_root = scrapy.Field()
    current_url = scrapy.Field()
    current_id = scrapy.Field()
    next_url = scrapy.Field()
    next_id = scrapy.Field()
    match_count = scrapy.Field()
    quality = scrapy.Field()
    high_quality = scrapy.Field()
    high_quality_scope = scrapy.Field()
    matched_href = scrapy.Field()
    matched_keywords = scrapy.Field()
    found_in = scrapy.Field()
    time_stamp = scrapy.Field()
    node_created = scrapy.Field()
