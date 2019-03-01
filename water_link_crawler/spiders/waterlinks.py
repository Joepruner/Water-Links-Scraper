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

# todo Exclude links that link back to current page.
# todo Create somekind of tree map showing all response url linked together.
# todo count number of match_urls per referer_url
# todo Find a way to check how "large" the content of the parent or grandparent is.


class WaterlinksSpider(CrawlSpider):
    name = 'waterlinks'
    start_urls = [
        'https://www.canadianwater.directory/bc/water-supply-resources']

    reject_href_regex = r"""(?imx)^(.*\#.*)$|^(\/)$|.*(\?).*|
        .*(login|regist(er)?(ration)?|advertisements?).*"""

    # todo How can this avoid looking for beggings of words that aren't words?
    match_words_regex = r"""(?imx)(?=((waste)?water|h2o|drink(ing)?|drainage|wells?|irrigat(e)?
        (ion)?(ing)?|hydrat(e)?(i(on)?(ng)?)?|pollut(ed)?(i(on)?(ng)?)))"""

    high_quality_match_regex = r"""(?ix)(?:water)(.){0,50}
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)|
        (?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)
        (.){0,50}(?:water)"""

    def write_headers():
        with open('links.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['referer', 'match_count', 'quality', 'high_quality',
                                 'high_quality_scope', 'link', 'relevent_text', 'found_in'])

    # todo override parse function, with own function that includes distance from root. 
    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')
        referer = response.url
        print (response.url)
        print (response.request.url, '\n')

        print('\n*******************************************\n')
        links_with_match_count = 0
        for link in soup:
            # todo calculate mod based on len(scope)
            scope = {
                'href': {'target': link.get('href'), 'mod': 2},
                'anchor': {'target': link, 'mod': 1.8},
                'anchor parent': {'target': link.parent, 'mod': .6}}
            # 'anchor grandparent':{'target':link.parent.parent,'mod':.3}}

            for key, value in scope.items():
                current_scope = value['target']
                href_self_target_check = re.match(
                    self.reject_href_regex, str(current_scope))
                if not href_self_target_check:
                    results = re.findall(
                        self.match_words_regex, str(current_scope))
                    if results:
                        # print(results,'\n')
                        matches = []
                        quality = 0
                        is_high_quality = False
                        high_quality_scope = 'N\A'
                        #todo Possibly rewrite search regex with ? operators so multiple matches in single result.
                        high_quality_check = re.search(
                            self.high_quality_match_regex, str(current_scope))
                        if (high_quality_check):
                            # todo Modify this to count multiple high-quality segments in scope. re.findall
                            # print("HIGH QUALITY")
                            quality += 10
                            is_high_quality = True
                            high_quality_scope = str(current_scope)

                        for i, a in enumerate(results):
                            # print(i, ' ', a[0],' , ',a[1], ' , ', a[2]);
                            # print(a);
                            # matches.append(a[0])
                            # quality += 1
                    
                            for i in range (0,len(results[0])):
                                if (a[i] != ''):
                                    matches.append(a[i])
                                    quality += 1
                        # print('\n')
                        quality += quality*value['mod']
                        # print('\n Matches' ,matches)

                        with open('links.csv', 'a', newline='') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',')
                            csv_writer.writerow([referer, len(matches), quality, is_high_quality, high_quality_scope, link.get('href'),
                                                 matches, key])
                        # il = ItemLoader(item=WaterLink(),response=response)
                        # il.add_value('referer_url',response.url)
                        # il.add_value('match_count',len(matches))
                        # il.add_value('quality', quality)
                        # il.add_value('high_quality', is_high_quality)
                        # il.add_value('high_quality_scope', high_quality_scope)
                        # il.add_value('match_url',link.get('href'))
                        # il.add_value('relevent_text', matches)
                        # il.add_value('found_in', key)
                        # yield il.load_item()
                        yield response.follow(link.get('href'), callback=self.parse)
                        links_with_match_count = links_with_match_count + 1
                        break
                else:
                    break

        print('\n Found',str(links_with_match_count),'matched links within current referer URL.')
        print('\n*******************************************\n')

WaterlinksSpider.write_headers()

# https://regex101.com/r/U7j8t1/7
#Okangan basin waterboard.
#How far from root.
#Where are duplictes found. 
#Email tomorrow. 