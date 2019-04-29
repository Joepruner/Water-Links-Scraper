# import scrapy
from multiprocessing import Process
from water_link_crawler.spiders.waterLinksSpider import WaterLinksSpider
from water_link_crawler.spiders.updateLinksSpider import UpdateLinksSpider as uls
from water_link_crawler.fill_nodes import FillNodes as fn
# from water_link_crawler.spider_home_base import SpiderHomeBase as shb
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import time

crawler_process = CrawlerProcess(get_project_settings())
crawler_process.crawl(WaterLinksSpider)

node_updater_process = Process(target=uls.get_headers)
node_filler_process = Process(target=fn.fill_nodes)

node_updater_process.start()

node_filler_process.start()


crawler_process.start()

#Explain Metrics check
#Overview of design check
#Lessons learned check
#Future direction check
#Add try catch blocks
#code comments
