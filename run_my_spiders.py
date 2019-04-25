# import scrapy
from water_link_crawler.spiders.waterLinksSpider import WaterlinksSpider
from water_link_crawler.fill_nodes import FillNodes as fn
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
import time

crawler_process = CrawlerProcess(get_project_settings())
crawler_process.crawl(WaterlinksSpider)
node_filler_multi_process = Process(target=fn.fill_nodes)

node_filler_multi_process.start()
crawler_process.start()
