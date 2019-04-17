# -*- coding: utf-8 -*-
import sys
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader
from water_link_crawler.items import WaterLink
import re
import csv
import pymongo
import json
import random
from neo4j import GraphDatabase


# todo Exclude links that link back to current page.
# todo Create somekind of tree map showing all response url linked together.
# todo count number of match_urls per referer_url
# todo Find a way to check how "large" the content of the parent or grandparent is.


class WaterlinksSpider(CrawlSpider):

    # def neo4j_connect():
    #     driver = GraphDatabase.driver(
    #         "bolt://localhost:7687", auth=("neo4j", "Skunkbrat9898!"))
    #     with driver.session() as session:
    #         session.run("create constraint on (link:Link) assert link.current_url is unique")
    link_id = 0

    name = 'waterlinks'
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


    def write_headers():
        with open('links.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['current_root', 'current_url' ,'next_url', 'match_count', 'quality', 'high_quality',
                'high_quality_scope', 'matched_keywords', 'found_in'])


    # todo override parse function, with own function that includes distance from root.
    def parse(self, response):


        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')
        # if len(response.meta['prev_root']) > 0:
        # previous_root = response.meta['item']
        current_root = re.findall(self.current_root_regex, str(response.url))

        # next_url = "TESTING"

        # print(response.url)
        # print(response.request.url, '\n')

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
                        # print('\n')

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
                        current_id = self.link_id + 1
                        next_id = self.link_id + 2
                        self.link_id += 2

                        # with open('links.csv', 'a', newline='') as csvfile:
                        #     csv_writer = csv.writer(csvfile, delimiter=',')
                        #     csv_writer.writerow([current_root, response.url, link.get('href'), len(matches), quality, is_high_quality, high_quality_scope,
                        #     matches, key])

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
                        il.add_value('matched_keywords', matches)
                        il.add_value('found_in', key)
                        yield il.load_item()

                        # print('\n*******************************************\n')
                        # print(response.url, "\n")
                        # print(link.get('href'), "\n")
                        # print('\n*******************************************\n')

                        request = response.follow(
                            link.get('href'), callback=self.parse)
                        yield request

                        links_with_match_count = links_with_match_count + 1
                        break
                else:
                    break

        # print('\n Found', str(links_with_match_count),
        #     'matched links within current referer URL.')
        # print('\n*******************************************\n')


# WaterlinksSpider.neo4j_connect()
WaterlinksSpider.write_headers()

# https://regex101.com/r/U7j8t1/7

# Okangan basin waterboard.
# How far from root.
# Where are duplictes found.

#Document purpose
#replace scope with good character distance measure