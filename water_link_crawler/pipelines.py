
from water_link_crawler.spiders.waterLinksSpider import WaterlinksSpider
from neo4j import GraphDatabase
from water_link_crawler.spider_home_base import SpiderHomeBase as shb
# from water_link_crawler.fill_nodes import FillNodes as fn
import os


class CreateNodeRelationships(object):

    #Add external credentials
    def __init__(self):
        self._driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "Skunkbrat9898!"))

    def close(self):
        self._driver.close()

    def process_item(self, item, spider):
        shb.save_node_item(item)


        #Boolean to check if URL has been visited before.
        current_already_visited = shb.checkVisited(item['current_url'][0])
        next_already_visited = shb.checkVisited(['next_url'][0])

        with self._driver.session() as session:
            if (not current_already_visited and not next_already_visited):
                session.run(
                    """create (curr:link {url: $current_url, node_id: $current_id})
                    create (next:link {url: $next_url, node_id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_url=item['current_url'][0], current_id=item['current_id'][0],
                    next_url=item['next_url'][0], next_id=item['next_id'][0])
                #Append URL/id key pair to visited URL dict.
                shb.makeVisited(item['current_url'][0], item['current_id'][0])
                shb.makeVisited(item['next_url'][0], item['next_id'][0])
            elif (not current_already_visited and next_already_visited):
                next_already_visited_id = shb.getUrlId(item['next_url'][0])
                session.run(
                    """create (curr:link {url: $current_url, node_id: $current_id})
                    with curr,
                    match(next:link {node_id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_url=item['current_url'][0], current_id=item['current_id'][0],
                    next_id=next_already_visited_id)
                shb.makeVisited(item['current_url'][0], item['current_id'][0])
            elif (current_already_visited and not next_already_visited):
                current_already_visited_id = shb.getUrlId(item['current_url'][0])
                session.run(
                    """create (next:link {url: $next_url, node_id: $next_id})
                    with next
                    match(curr:link {node_id: $current_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    next_url=item['next_url'][0], next_id=item['next_id'][0],
                    current_id=current_already_visited_id)
                shb.makeVisited(item['next_url'][0], item['next_id'][0])
            elif (current_already_visited and next_already_visited):
                current_already_visited_id = shb.getUrlId(item['current_url'][0])
                next_already_visited_id = shb.getUrlId(item['next_url'][0])
                session.run(
                    """match(curr:link {node_id: $current_id})
                    match(next:link {node_id: $next_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    current_id=current_already_visited_id,
                    next_id=next_already_visited_id)



        #shb.viewNodeData()
        #print("\n***************POPPED\n",fn.get_node_data_queue(),"\n***************POPPED\n")



#visited timestamp and flag.
#Do a conditional GET to check timestamp for updates.
#paralellism: One thread creates nodes, while another thread fills them.
#If a link without any water description is found, search up to a paragraph
#-ahead and behind for key word data.

#20 hops deep limit

#My Thoughts:
#-I think a list of all visited URL's must be maintained, because we need to be able to
#search in that list to avoid duplicates

