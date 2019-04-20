
from neo4j import GraphDatabase
from water_link_crawler.spider_home_base import SpiderHomeBase as shb

class FillNodes():

    def __init__(self):
        self._driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "Skunkbrat9898!"))

    def _close(self):
        self._driver.close()

    def _fill_node(self):
        data = shb.pop_node_data_queue()
        print("\n***************\n",data,"\n***************\n")
        with self._driver.session() as session:
            session.run(
                    """match(n:link {node_id: $id})

                    set n.root = $root
                    set n.quality = $quality
                    set n.high_quality = $high_quality
                    set n.high_quality_scope = $high_quality_scope
                    set n.matched_keywords = $matched_keywords
                    set n.match_count = $match_count
                    set n.found_in = $found_in
                    set n.time_stamp = $time_stamp
                    set n.node_filled = $node_filled""",
                    id=data['current_id'][0],
                    root=data['current_root'][0],
                    quality=data['quality'][0],
                    high_quality=data['high_quality'][0],
                    high_quality_scope=data['high_quality_scope'][0],
                    matched_keywords=data['matched_keywords'][0],
                    match_count=data['match_count'][0],
                    found_in=data['found_in'][0],
                    time_stamp=data['time_stamp'][0],
                    node_filled=True)


