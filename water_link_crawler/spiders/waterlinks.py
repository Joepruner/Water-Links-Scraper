# -*- coding: utf-8 -*-
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
# todo Fix regex to check if includes ANY of keywords
# todo get relevent text
# todo load items
# todo count number of match_urls per referer_url

# https://www.bcwwa.org/news-announcements/tags/waterquality,1,33,True,waterquality,['water'],href
# https://www.bcwwa.org/news-announcements/tags/waterquality,1,3,False,/news-announcements/tags/waterquality,['water'],href


class WaterlinksSpider(CrawlSpider):
    name = 'waterlinks'
    start_urls = [
        'https://www.canadianwater.directory/bc/water-supply-resources']
    reject_href_regex = r'(?imx)^(.*[\#].*)$|^([\/])$|.*(login|regist(er)?(ration)?|advertisements?).*'
    search_words_regex = r"""(?imx)(?=((waste)?water|h2o|drink(ing)?|drainage|wells?|irrigat(e)?
        (ion)?(ing)?|hydrat(e)?(i(on)?(ng)?)?|pollut(ed)?(i(on)?(ng)?)))"""



    high_quality_match_regex_left = r"""(?ix)(?:water)(.){0,50}
(?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)|
(?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|resources?)(.){0,50}(?:water)"""
    # high_quality_match_regex_right = r"""(?im)(?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|suppliers?)(?:\w*?\W*?){0,6}(?:water)"""

# (?:water)(?:\w*?\W*?){0,6}(?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|suppliers?)|(?:qualit(ies)?y?|grades?|conditions?|make-?up|classifications?|ranks?|suppliers?)(?:\w*?\W*?){0,6}(?:water)



    def write_headers():
        with open('links.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['referer', 'match_count', 'quality', 'high_quality', 'high_quality_scope', 'link', 'relevent_text', 'found_in'])

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find_all('a')
        referer = response.url

        print('\n*******************************************\n')
        link_count = 0
        # scope_labels = ['href', 'anchor', 'anchor parent', 'anchor grandparent']
        for link in soup:
            scope = {
                'href':{'target':link.get('href'), 'mod':2},
                'anchor':{'target':link, 'mod':1.8},
                'anchor parent':{'target':link.parent, 'mod':.6}}
                # 'anchor grandparent':{'target':link.parent.parent,'mod':.3}}
            # print(re.search(search_words_regex, str(link),flags=regex_flags))
            quality_modifier = 1;
            for key, value in scope.items():
                current_scope=value['target']

                href_self_target_check = re.match(self.reject_href_regex,str(current_scope))
                if not href_self_target_check:
                    results = re.findall(self.search_words_regex,str(current_scope))
                    if results:
                        # print(current_scope,'\n\n\n')
                        matches = []
                        quality = 0
                        is_high_quality = False
                        high_quality_scope = 'N\A'
                        high_quality_check = re.search(self.high_quality_match_regex_left,str(current_scope))
                        print(high_quality_check)
                        if (high_quality_check):
                            print("HIGH QUALITY")
                            quality += 10
                            is_high_quality = True
                            high_quality_scope = str(current_scope)
                        for i,a in enumerate(results):
                            # print (i, ":",a[2])
                            matches.append(a[0])
                            quality += 1
                        quality += quality*value['mod']

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
                        yield response.follow(link.get('href'), callback = self.parse)
                        link_count = link_count + 1
                        break
                else:
                    break
                quality_modifier -= .29

        print('\n Links found: '+str(link_count))
        print('\n*******************************************\n')


WaterlinksSpider.write_headers()

# https://regex101.com/r/U7j8t1/7

 # rules = (
    #     Rule(LinkExtractor(restrict_xpaths="//a[@class='alphadex_item-link'"), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(restrict_xpaths="//a[@class='pagination__button pagination__next-button'"), callback='parse_item', follow=True),
    # )
