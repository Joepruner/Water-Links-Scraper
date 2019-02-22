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
# from water_link_crawler.items import items
# Ideas: Find links, and then look at first few parents for
# water language.

# todo Exclude links that link back to current page.
# todo Create somekind of tree map showing all response url linked together.
# todo Fix regex to check if includes ANY of keywords
# todo get relevent text
# todo load items
# todo count number of match_urls per referer_url


class WaterlinksSpider(CrawlSpider):
    name = 'waterlinks'
    start_urls = [
        'https://www.canadianwater.directory/bc/water-supply-resources']
    search_words_regex = r'(?is)(?!.*?(\#))(?!.*?\b(advertisement)\b)(?=\b(water|drinking|drainage|well(s)?)\b)'
    # (?is)^(?=.*?\b(water|supply)\b)(?!.*?#).*'
        # (?=.*?\b(boogers)\b)
    # (?=.*\bdrinking\b|\birrigation\b|drainage\b|\bresources\b).*'
# ^(?=.*^(?!.*#).*$)(?=.*^(?!.*advertisement).*$)
    def write_headers():
        with open('links.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['referer', 'link', 'relevent_text', 'found_in'])

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')
        referer = response.url

        print('\n*******************************************\n')
        link_count = 0
        # scope_labels = ['href', 'anchor', 'anchor parent', 'anchor grandparent']
        for link in soup.find_all('a'):
            scope = {'href':link.get('href'),'anchor':link, 'anchor parent':link.parent}
            # , 'anchor grandparent':link.parent.parent}
            # print(re.search(search_words_regex, str(link),flags=regex_flags))
            for key, value in scope.items():
                results = re.findall(self.search_words_regex,str(value))
                il = ItemLoader(item=WaterLink(),response=response)
                if results:
                    matches = []
                    for i,a in enumerate(results):
                        # print (i, ":",a[2])
                        matches.append(a[2])
                    # print(matches)
                    # print(re.findall(self.search_words_regex,str(value)))
                    # with open('links.csv', 'a', newline='') as csvfile:
                    #     csv_writer = csv.writer(csvfile, delimiter=',')
                    #     csv_writer.writerow([referer, link.get('href'),
                    #     matches, key])
                    il.add_value('referer_url',response.url)
                    il.add_value('match_url',link.get('href'))
                    il.add_value('relevent_text', matches)
                    il.add_value('found_in', key)
                    yield il.load_item()
                    # yield response.follow(link.get('href'), callback = self.parse)
                    link_count = link_count + 1
                    # print(value,'\n')
                    break

        print('\n Links found: '+str(link_count))
        print('\n*******************************************\n')


WaterlinksSpider.write_headers()



 # rules = (
    #     Rule(LinkExtractor(restrict_xpaths="//a[@class='alphadex_item-link'"), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(restrict_xpaths="//a[@class='pagination__button pagination__next-button'"), callback='parse_item', follow=True),
    # )



              # elif(re.search(search_words_regex, str(link), flags=re.I)):
                #     with open('links.csv', 'a', newline='') as csvfile:
                #         csv_writer = csv.writer(csvfile, delimiter=',')
                #         csv_writer.writerow([referer, link.get('href')])
                #     yield response.follow(link.get('href'), callback = self.parse)
                #     link_count = link_count + 1
                # elif(re.search(search_words_regex, str(link.parent), flags=re.I)):
                #     with open('links.csv', 'a', newline='') as csvfile:
                #         csv_writer = csv.writer(csvfile, delimiter=',')
                #         csv_writer.writerow([referer, link.get('href')])
                #     yield response.follow(link.get('href'), callback = self.parse)
                #     link_count = link_count + 1
                # elif(re.search(search_words_regex, str(link.parent.parent), flags=re.I)):
                #     with open('links.csv', 'a', newline='') as csvfile:
                #         csv_writer = csv.writer(csvfile, delimiter=',')
                #         csv_writer.writerow([referer, link.get('href')])
                #     yield response.follow(link.get('href'), callback = self.parse)
                #     link_count = link_count + 1
