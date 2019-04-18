# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from water_link_crawler.spiders.waterlinks import WaterlinksSpider
from neo4j import GraphDatabase
import multiprocessing
import os


class WaterLinkCrawlerPipeline(object):

    visited_links = {}
    node_data = {}



    #Add external credentials
    def __init__(self):
        self._driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "Skunkbrat9898!"))

    def close(self):
        self._driver.close()

    def process_item(self, item, spider):

        self.node_data[item['current_id'][0]] = item

        #print("\n","\n","\n",self.node_data,"\n","\n","\n")

        #Boolean to check if URL has been visited before.
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
                #Append URL/id key pair to visited URL dict.
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

    # def fill_nodes(self, item, spider):
    #     if self.node_data.__len__ == 0:
    #         return
    #     else:
    #         for node in self.node_data:
    #             if self.node_data[0]




            # if (item['current_id'][0] in self.node_data):
            #     print("\n","\n","\n","\n","\n",item['current_id'])
            #     print(self.node_data[item['current_id'][0]],"\n","\n","\n")


#visited timestamp and flag.
#Do a conditional GET to check timestamp for updates.
#paralellism: One thread creates nodes, while another thread fills them.
#If a link without any water description is found, search up to a paragraph
#-ahead and behind for key word data.

#20 hops deep limit

#My Thoughts:
#-I think a list of all visited URL's must be maintained, because we need to be able to
#search in that list to avoid duplicates

