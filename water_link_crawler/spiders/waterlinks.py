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

# todo Exclude links that link back to current page.
# todo Create somekind of tree map showing all response url linked together.
# todo count number of match_urls per referer_url
# todo Find a way to check how "large" the content of the parent or grandparent is.


class WaterlinksSpider(CrawlSpider):
    name = 'waterlinks'
    start_urls = ['https://www.obwb.ca/']
    reject_href_regex = r"""(?imx)^(.*\#.*)$|^(\/)$|.*(\?).*|
        .*(login|regist(er)?(ration)?|advertisements?).*"""

    # todo How can this avoid looking for begginings of words that aren't words?
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
            csv_writer.writerow(['previous_url','current_root', 'current_page', 'match_count', 'quality', 'high_quality',
                                 'high_quality_scope', 'matched_href', 'matched_keywords', 'found_in', 'hops_from_start_root','next_url'])

    # todo override parse function, with own function that includes distance from root.
    def parse(self, response):

        # hops_from_start_root
        # hops_from_start_root += 0

        # self.num_test.append(random.randint(1,10))

        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')
        # if len(response.meta['prev_root']) > 0: 
        # previous_root = response.meta['item']
        current_page = response.url
        current_root = re.findall(self.current_root_regex, str(current_page))

        # self.root_list.append(current_root)
        # if current_page not in self.root_list:
            
        

        # item = response.meta['item']
        # item['other_url'] = response.url
        # yield item

        if self.referer_root != current_root:
            self.referer_root = current_root
            self.hops_from_start_root += 1

        print(response.url)
        print(response.request.url, '\n')

        print('\n*******************************************\n')
        links_with_match_count = 0
        for link in soup:
            # todo calculate mod based on len(scope)?
            quality = 0
            is_high_quality = False
            high_quality_scope = 'N\A'
            matches = []
            write = False
            scope = {
                'href': {'target': link.get('href'), 'mod': 2},
                'anchor': {'target': link, 'mod': 1.8},
                'anchor_parent': {'target': link.parent, 'mod': .6},
                'anchor_grandparent': {'target': link.parent.parent, 'mod':.3}}

            for key, value in scope.items():
                current_scope = value['target']
                href_self_target_check = re.match(
                    self.reject_href_regex, str(current_scope))
                if not href_self_target_check:
                    results = re.findall(
                        self.match_words_regex, str(current_scope))
                    high_quality_check = re.search(
                        self.high_quality_match_regex, str(current_scope))

                    # todo find better fix for large scopes.
                    if results and len(str(current_scope)) < 150:
                        write = True
                        # todo Possibly rewrite search regex with ? operators so multiple matches in single result.
                        for i, a in enumerate(results):
                            for i in range(0, len(results[0])):
                                if (a[i] != ''):
                                    matches.append(a[i])
                                    quality += 1
                        # print('\n')

                    # todo Modify this to count multiple high-quality segments in scope. re.findall
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

                    if write == True and quality > quality_threshold:

                        # with open('links.csv', 'a', newline='') as csvfile:
                        #     csv_writer = csv.writer(csvfile, delimiter=',')
                        #     csv_writer.writerow([previous_url, current_root, current_page, len(matches), quality, is_high_quality, high_quality_scope, link.get('href'),
                        #                          matches, key, self.hops_from_start_root,next_url])
                        il = ItemLoader(item=WaterLink(),response=response)
                        il.add_value('previous_url',response.url)
                        il.add_value('current_root',current_root)
                        il.add_value('current_page',current_page)
                        il.add_value('match_count',len(matches))
                        il.add_value('quality', quality)
                        il.add_value('high_quality', is_high_quality)
                        il.add_value('high_quality_scope', high_quality_scope)
                        il.add_value('matched_href',link.get('href'))
                        il.add_value('matched_keywords', matches)
                        il.add_value('found_in', key)
                        il.add_value('next_url', next_url)
                        yield il.load_item()

                    # item = MyItem()
                    #     item['main_url'] = response.url
                    #     request = scrapy.Request("http://www.example.com/some_page.html",
                    #                             callback=self.parse_page2)
                    #     request.meta['item'] = item
                    #     yield request
                        # item = MyItem()
                        # item['prev_root'] = current_root
                        request = response.follow(link.get('href'), callback=self.parse)
                        # request.meta['item'] = item
                        yield request

                        print(self.root_list)
                        # print(self.num_test)
                        links_with_match_count = links_with_match_count + 1
                        break
                else:
                    break

        print('\n Found', str(links_with_match_count),
              'matched links within current referer URL.')
        print('\n*******************************************\n')


WaterlinksSpider.write_headers()

# https://regex101.com/r/U7j8t1/7
# Okangan basin waterboard.
# How far from root.
# Where are duplictes found.
