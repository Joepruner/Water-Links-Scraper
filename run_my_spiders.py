# import scrapy
from water_link_crawler.spiders.waterLinksSpider import WaterlinksSpider
from water_link_crawler.fill_nodes import FillNodes as fn
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process
import time






# timeout = time.time() + 3

crawler_process = CrawlerProcess(get_project_settings())
crawler_process.crawl(WaterlinksSpider)
node_filler_multi_process = Process(target=fn.fill_nodes)

node_filler_multi_process.start()
crawler_process.start()
# spider_1_process = Process(target=crawler_process.start())
# crawler_process.start()
# while True:
#     if time.time() > timeout:
#         print("*************STOPPING**************")
#         crawler_process.stop()
#         node_filler_process.start()
#         break




