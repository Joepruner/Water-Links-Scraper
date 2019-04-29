# -*- coding: utf-8 -*-
# import sys
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from water_link_crawler.spiders.waterLinksSpider import WaterLinksSpider
# from scrapy import http
# from scrapy import Request
from multiprocessing import Queue
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader

import certifi
import urllib3

from water_link_crawler.spider_home_base import SpiderHomeBase as shb
import re
import random
from neo4j import GraphDatabase
import datetime
import time
from water_link_crawler import settings
import os


class UpdateLinksSpider(CrawlSpider):

    name = 'update_spider'
    _driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    time_format = "%d%m%Y%H%M%S"

    #get URL Headers to check Last-Modified
    @classmethod
    def get_headers(cls):
        while True:
            time.sleep(2)
            #Get the list of all visited links.
            visited = shb.get_all_visited()
            while visited.empty() == False:
                visited_url = visited.get()
                url_response = cls.http.request('GET', visited_url)
                cls.check_modified(url_response.headers, url_response, visited_url)
    @classmethod
    def check_modified(cls, headers, url_response, visited_url):
        print("Checking headers")
        with cls._driver.session() as session:
            db_node_data = session.run(
                """match(n:link {url: $url})
                return n.timestamp""",url=visited_url)
            db_node_timestamp = db_node_data.data()[0]['n.timestamp']
            # db_node_id = db_node_data.data()[0]['node_id']
            # make needs update field
        # try:
            # if datetime.strptime(headers['Last-Modified'],cls.time_format) > db_node_timestamp:
            if True:
                shb._save_needs_update(visited_url)
                print("Last-Modified timestamp is more recent than database timestamp - Updating node")
            else:
                print("Last-Modified timestamp is older than database timestamp.")
        # except:
            # print("No Last-Modified header provided.")
