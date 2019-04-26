# -*- coding: utf-8 -*-
# import sys
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
# from scrapy import http
# from scrapy import Request
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader

import urllib3
from water_link_crawler.spider_home_base import SpiderHomeBase as shb
import re
import random
from neo4j import GraphDatabase
import datetime
import time


class UpdatedLink(object):

    def __init__(self,quality, high_quality, high_quality_scope,
        match_count, found_id, time_stamp):

        self.quality = quality
        self.high_quality = high_quality
        self.high_quality_scope = high_quality_scope
        self.match_count = match_count
        self.found_in = found_in
        self.time_stamp = time_stamp


class UpdateLinksSpider(CrawlSpider):

    # link_id = 1
    name = 'update_spider'
    # start_urls = shb.get_all_visited()
    _driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("fill_nodes", "neo_fill_nodes"))
    http = urllib3.PoolManager()

    reject_href_regex = r"""(?imx)^(.*\#.*)$|^(\/)$|.*(\?).*|
        .*(login|regist(er)?(ration)?|advertisements?|\.jp(e)?g?|\.png|\.gif|\.tiff).*"""
    match_words_regex = r"""(?imx)(?=((waste)?water|h2o|drink(ing)?|drainage|wells?|irrigat(e)?
        (ion)?(ing)?|hydrat(e)?(i(on)?(ng)?)?|pollut(ed)?(i(on)?(ng)?)))"""
    high_quality_match_regex = r"""(?ix)(?:water)(.){0,50}
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)|
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)
        (.){0,50}(?:water)"""
    current_root_regex = r'(?ix)^http.?://.*?/'

    @classmethod
    def get_headers(cls):

        while True:
            # print('*********INSIDE LOOP',shb.get_all_visited(),'**************')
            time.sleep(3)
            visited = shb.get_all_visited()
            while visited.empty() == False:
                link = visited.get()
                # cls.curr_link = link
                print(link)
                with cls._driver.session() as session:
                    db_time = session.run(
                        """match(n:link {url: $url})
                        return n.time_stamp""",
                        url=link)
                    # print('\n************',db_time,'**********\n')

                response = http.request('GET', link)
                print(response.headers)
                # yield Request(link, cls.check_modified(link), method='HEAD' )
                cls.check_modified(response)
                # print(response.header['Last-Modified'])
                # if headers['Last-Modified']
    @classmethod
    def check_modified(cls):
        print("Hello")
        # with cls._driver.session() as session:
        #     db_time = session.run(
        #     """match(n:link {url: $url})
        #     return n.time_stamp""",url=link)

    # todo override parse function, with own function that includes distance from root.
    @classmethod
    def update_link(cls, response):


        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')

        current_root = re.findall(cls.current_root_regex, str(response.url))

        shb.get_all_visited()
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
                href_cls_target_check = re.match(
                    cls.reject_href_regex, str(current_scope))
                if not href_cls_target_check:
                    results = re.findall(
                        cls.match_words_regex, str(current_scope))
                    high_quality_check = re.search(
                        cls.high_quality_match_regex, str(current_scope))

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
                        current_id = cls.link_id
                        next_id = cls.link_id + 1
                        cls.link_id += 1
                        now = datetime.datetime.now()
                        date_time = now.strftime("%Y%m%d%H%M%S")


                        item = UpdatedLink(quality, is_high_quality, high_quality_scope,
                        len(matches),key, date_time)

                        # il.add_value('match_count', len(matches))
                        # il.add_value('quality', quality)
                        # il.add_value('high_quality', is_high_quality)
                        # il.add_value('high_quality_scope', high_quality_scope)
                        # il.add_value('matched_keywords', matches)
                        # il.add_value('found_in', key)
                        # il.add_value('time_stamp', date_time)
                        # il.add_value('node_filled', False)
                        # yield il.load_item()

                        # request = response.follow(
                        #     link.get('href'), callback=cls.parse)
                        # yield request

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