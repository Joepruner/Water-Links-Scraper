from neo4j import GraphDatabase
from multiprocessing import Queue


#class for multiple, concurrent spiders to track URL and node information
class SpiderHomeBase():
    visited_links = {}
    node_data_queue = Queue()

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
        cls.node_data_queue.put(item)
        # cls.node_data_queue.append("5")

    # @classmethod
    # def view_node_data_queue(cls):
    #     print("\n***************\n",cls.node_data_queue"\n***************\n")

    @classmethod
    def get_node_data(cls):
        # if cls.node_data_queue.empty():
        #     return False
        # else:
        return cls.node_data_queue.get()

    @classmethod
    def node_data_queue_length(cls):
        print("**********QUEUE LENGTH****************\n", cls.node_data_queue.qsize())
        # time.sleep(5)
        # return cls.node_data_queue.qsize()

    @classmethod
    def is_queue_empty(cls):
        return cls.node_data_queue.empty()