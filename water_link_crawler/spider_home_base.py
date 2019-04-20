from neo4j import GraphDatabase


#class for multiple, concurrent spiders to track URL and node information
class SpiderHomeBase():
    visited_links = {}
    node_data_queue = []

    @classmethod
    def checkVisited (cls, url):
        if url in cls.visited_links:
            return True
        else:
            return False

    @classmethod
    def getUrlId (cls, url):
        id = cls.visited_links[url]
        return id

    @classmethod
    def makeVisited (cls, url, id):
        cls.visited_links[url] = id

    @classmethod
    def save_node_item (cls, item):
        cls.node_data_queue.append(item)

    @classmethod
    def view_node_data_queue(cls):
        print("\n***************\n",cls.node_data_queue,"\n***************\n")

    @classmethod
    def pop_node_data_queue(cls):
        if not cls.node_data_queue:
            return False
        else:
            return cls.node_data_queue.pop(0)

    @classmethod
    def node_data_queue_length(cls):
        return len(cls.node_data_queue)