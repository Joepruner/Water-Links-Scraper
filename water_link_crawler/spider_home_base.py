from neo4j import GraphDatabase
from multiprocessing import Queue


#class for multiple, concurrent spiders to track URL and node information
class SpiderHomeBase():
    _visited_links = {}
    _node_data_queue = Queue()

    _root_created = False

    @classmethod
    def is_root_created(cls):
        return cls._root_created

    @classmethod
    def root_created(cls):
        cls._root_created = True

    @classmethod
    def checkVisited (cls, url):
        if url in cls._visited_links:
            return True
        else:
            return False

    @classmethod
    def getUrlId (cls, url):
        id = cls._visited_links[url]
        return id

    @classmethod
    def makeVisited (cls, url, id):
        cls._visited_links[url] = id

    @classmethod
    def save_node_item (cls, item):
        cls._node_data_queue.put(item)
        # cls.node_data_queue.append("5")

    @classmethod
    def get_node_data(cls):
        # if cls.node_data_queue.empty():
        #     return False
        # else:
        return cls._node_data_queue.get()

    @classmethod
    def node_data_queue_length(cls):
        print("**********QUEUE LENGTH****************\n",
            cls._node_data_queue.qsize())

    @classmethod
    def is_queue_empty(cls):
        return cls._node_data_queue.empty()