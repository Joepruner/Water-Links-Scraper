# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from water_link_crawler.spiders.waterlinks import WaterlinksSpider
from neo4j import GraphDatabase


class WaterLinkCrawlerPipeline(object):

    visited_links = {}


    #Add external credentials
    def __init__(self):
        self._driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "Skunkbrat9898!"))

    def close(self):
        self._driver.close()

    # def increment_id(self):
    #     new_id = self.link_id +1
    #     self.link_id = new_id
    #     return self.link_id

    def process_item(self, item, spider):

        # if (item['current_url'] == item['next_url']):
        #     return

        current_already_visited = item['current_url'][0] in self.visited_links
        next_already_visited = item['next_url'][0] in self.visited_links

        with self._driver.session() as session:
            if (not current_already_visited and not next_already_visited):
                session.run(
                    """create (curr:link {url: $current_url, id: $current_id})
                    create (next:link {url: $next_url, id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_url=item['current_url'][0], current_id=item['current_id'],
                    next_url=item['next_url'][0], next_id=item['next_id'])
                self.visited_links[item['current_url'][0]] = item['current_id']
                self.visited_links[item['next_url'][0]] = item['next_id']
            elif (not current_already_visited and next_already_visited):
                next_already_visited_id = self.visited_links[item['next_url'][0]]
                session.run(
                    """create (curr:link {url: $current_url, id: $current_id})
                    with curr,
                    match(next:link {id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_url=item['current_url'][0], current_id=item['current_id'],
                    next_id=next_already_visited_id)
                self.visited_links[item['current_url'][0]] = item['current_id']
            elif (current_already_visited and not next_already_visited):
                current_already_visited_id = self.visited_links[item['current_url'][0]]
                session.run(
                    """create (next:link {url: $next_url, id: $next_id})
                    with next
                    match(curr:link {id: $current_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    next_url=item['next_url'][0], next_id=item['next_id'],
                    current_id=current_already_visited_id)
                self.visited_links[item['next_url'][0]] = item['next_id']
            elif (current_already_visited and next_already_visited):
                current_already_visited_id = self.visited_links[item['current_url'][0]]
                next_already_visited_id = self.visited_links[item['next_url'][0]]
                session.run(
                    """match(curr:link {id: $current_id})
                    match(next:link {id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_id=current_already_visited_id,
                    next_id=next_already_visited_id)

#Distance


#visited timestamp and flag.
#Do a conditional GET to check timestamp for updates.
#paralellism: One thread creates nodes, while another thread fills them.
#If a link without any water description is found, search up to a paragraph
#-ahead and behind for key word data. 

#20 hops deep limit
