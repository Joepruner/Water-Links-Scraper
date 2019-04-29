
from neo4j import GraphDatabase
from water_link_crawler.spiders.waterLinksSpider import WaterLinksSpider as wls
from water_link_crawler.spider_home_base import SpiderHomeBase as shb
from water_link_crawler import settings
import time
import os

class FillNodes():

    @classmethod
    def fill_nodes(cls):
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

        while True:

            time.sleep(2)

            shb.node_data_queue_length()

            while not shb.is_queue_empty():
                data = shb.get_node_data()


                with _driver.session() as session:

                    session.run(
                        """match(n:link {node_id: $id})
                        set n.root = $root
                        set n.quality = $quality
                        set n.high_quality = $high_quality
                        set n.high_quality_scope = $high_quality_scope

                        set n.match_count = $match_count
                        set n.found_in = $found_in
                        set n.timestamp = $timestamp
                        set n.needs_update = $needs_update""",
                        id=data['current_id'][0],
                        root=data['current_root'][0],
                        quality=data['quality'][0],
                        high_quality=data['high_quality'][0],
                        high_quality_scope=data['high_quality_scope'][0],
                        # matched_keywords=data['matched_keywords'][0],
                        match_count=data['match_count'][0],
                        found_in=data['found_in'][0],
                        timestamp=data['timestamp'][0],
                        needs_update=data['needs_update'][0])

# set n.matched_keywords = $matched_keywords


