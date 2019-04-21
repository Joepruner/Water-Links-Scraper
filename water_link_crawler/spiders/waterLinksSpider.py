# -*- coding: utf-8 -*-
# import sys
import scrapy
from scrapy.spiders import CrawlSpider, Rule
#from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader
# from scrapy.utils.project import get_project_settings
#from water_link_crawler.items import WaterLink
import re
import random
from neo4j import GraphDatabase
import datetime


# todo Exclude links that link back to current page.
# todo Create somekind of tree map showing all response url linked together.
# todo count number of match_urls per referer_url
# todo Find a way to check how "large" the content of the parent or grandparent is.

class WaterLink(scrapy.Item):
    current_root = scrapy.Field()
    current_id = scrapy.Field()
    current_url = scrapy.Field()
    next_id = scrapy.Field()
    next_url = scrapy.Field()
    quality = scrapy.Field()
    high_quality = scrapy.Field()
    high_quality_scope = scrapy.Field()
    # matched_keywords = scrapy.Field()
    match_count = scrapy.Field()
    found_in = scrapy.Field()
    # time_stamp = scrapy.Field()
    node_filled = scrapy.Field()


class WaterlinksSpider(CrawlSpider):

    link_id = 1

    name = 'water_spider_1'
    start_urls = ['https://www.obwb.ca/']

    reject_href_regex = r"""(?imx)^(.*\#.*)$|^(\/)$|.*(\?).*|
        .*(login|regist(er)?(ration)?|advertisements?|\.jp(e)?g?|\.png|\.gif|\.tiff).*"""
    match_words_regex = r"""(?imx)(?=((waste)?water|h2o|drink(ing)?|drainage|wells?|irrigat(e)?
        (ion)?(ing)?|hydrat(e)?(i(on)?(ng)?)?|pollut(ed)?(i(on)?(ng)?)))"""
    high_quality_match_regex = r"""(?ix)(?:water)(.){0,50}
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)|
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)
        (.){0,50}(?:water)"""
    current_root_regex = r'(?ix)^http.?://.*?/'

    # todo override parse function, with own function that includes distance from root.
    def parse(self, response):


        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')

        current_root = re.findall(self.current_root_regex, str(response.url))

        print('\n*******************************************\n')
        links_with_match_count = 0
        for link in soup:
            quality = 0
            is_high_quality = False
            high_quality_scope = 'N\A'
            matches = []
            write = False
            scope = {
                'href': {'target': link.get('href'), 'mod': 2},
                'anchor': {'target': link, 'mod': 1.8},
                'anchor_parent': {'target': link.parent, 'mod': .6},
                'anchor_grandparent': {'target': link.parent.parent, 'mod': .3}}

            for key, value in scope.items():
                current_scope = value['target']
                href_self_target_check = re.match(
                    self.reject_href_regex, str(current_scope))
                if not href_self_target_check:
                    results = re.findall(
                        self.match_words_regex, str(current_scope))
                    high_quality_check = re.search(
                        self.high_quality_match_regex, str(current_scope))

                    if results and len(str(current_scope)) < 150:
                        write = True
                        for i, a in enumerate(results):
                            for i in range(0, len(results[0])):
                                if (a[i] != ''):
                                    matches.append(a[i])
                                    quality += 1

                    if high_quality_check and len(str(current_scope)) < 200:
                        write = True
                        quality += 10
                        is_high_quality = True
                        high_quality_scope = str(current_scope)

                    quality = quality*value['mod']

                    if key == 'anchor_parent' or key == 'anchor_grandparent':
                        quality_threshold = 4
                    else:
                        quality_threshold = 0

                    if write == True and quality > quality_threshold and (response.url != link.get('href')):
                        current_id = self.link_id
                        next_id = self.link_id + 1
                        self.link_id += 1

                        il = ItemLoader(item=WaterLink(), response=response)
                        il.add_value('current_root', current_root)
                        il.add_value('current_url', response.url)
                        il.add_value('current_id', current_id)
                        il.add_value('next_url', link.get('href'))
                        il.add_value('next_id', next_id)
                        il.add_value('match_count', len(matches))
                        il.add_value('quality', quality)
                        il.add_value('high_quality', is_high_quality)
                        il.add_value('high_quality_scope', high_quality_scope)
                        # il.add_value('matched_keywords', matches)
                        il.add_value('found_in', key)
                        # il.add_value('time_stamp', datetime.datetime.now())
                        il.add_value('node_filled', False)
                        yield il.load_item()

                        request = response.follow(
                            link.get('href'), callback=self.parse)
                        yield request

                        links_with_match_count = links_with_match_count + 1
                        break
                else:
                    break





# https://regex101.com/r/U7j8t1/7

# Okangan basin waterboard.
# How far from root.
# Where are duplictes found.

#Document purpose
#replace scope with good character distance measure