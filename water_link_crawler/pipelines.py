
from water_link_crawler.spiders.waterLinksSpider import WaterLinksSpider as wls
from neo4j import GraphDatabase
from water_link_crawler import settings
from water_link_crawler.spider_home_base import SpiderHomeBase as shb
import os


class CreateNodeRelationships(object):

    #Add external credentials
    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

    def close(self):
        self._driver.close()

    def process_item(self, item, spider):
        shb.save_node_item(item)

        #Boolean to check if URL has been visited before.
        current_already_visited = shb.checkVisited(item['current_url'][0])
        next_already_visited = shb.checkVisited(['next_url'][0])

        with self._driver.session() as session:
            #If this item is the root node
            if (not shb.is_root_created() and item['current_url'][0] ==  wls.start_urls[0]
            and not next_already_visited):
                shb.root_created()

                session.run(
                    """create (curr:link {url: $current_url, node_id: $current_id, hops_from_root: $hops})""",
                    # create (next:link {url: $next_url, node_id: $next_id, hops_from_root: $next_hops})
                    # merge (curr)-[r:LINKS_TO]->(next)
                    current_url=item['current_url'][0], current_id=item['current_id'][0], hops=0)
                    # next_url=item['next_url'][0], next_id=item['next_id'][0], next_hops=1)
                #Append URL/id key pair to visited URL dict.
                shb.makeVisited(item['current_url'][0], item['current_id'][0])
                # shb.makeVisited('www.weewawow.com', 7)
                # shb.makeVisited(item['next_url'][0], item['next_id'][0])


            if (current_already_visited and not next_already_visited):
                current_already_visited_id = shb.getUrlId(item['current_url'][0])

                curr_hop_num = session.run(
                    """match(n:link {node_id: $id})
                    return n.hops_from_root""",
                    id=current_already_visited_id
                    )
                # print(curr_hop_num.data()[0]['n.hops_from_root'])

                curr_hop_num = curr_hop_num.data()[0]['n.hops_from_root']
                next_hop_num = curr_hop_num
                next_hop_num += 1
                # print(curr_hop_num,"************\n")
                # print(next_hop_num)

                session.run(
                    """create (next:link {url: $next_url, node_id: $next_id, hops_from_root: $next_hops})
                    with next
                    match(curr:link {node_id: $current_id})
                    merge (curr)-[r:LINKS_TO]->(next)""",
                    next_url=item['next_url'][0], next_id=item['next_id'][0], next_hops=next_hop_num,
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
            shb.get_all_visited()



        #shb.viewNodeData()
        #print("\n***************POPPED\n",fn.get_node_data_queue(),"\n***************POPPED\n")


#todo clean up zombie processes

#visited timestamp and flag.
#Do a conditional GET to check timestamp for updates.
#paralellism: One thread creates nodes, while another thread fills them.
#If a link without any water description is found, search up to a paragraph
#-ahead and behind for key word data.

#20 hops deep limit