from neo4j import GraphDatabase
import multiprocessing
from multiprocessing import Queue


#class for multiple, concurrent spiders or classes to track URL and node information
class SpiderHomeBase():
    manager = multiprocessing.Manager()
    manager2 = multiprocessing.Manager()
    _visited_links = {}
    _visited_links_queue = manager.Queue()
    _needs_update_queue = manager2.Queue()


    _node_data_queue = Queue()
    _root_created = False

#*********** URL functions *********

    @classmethod
    def is_root_created(cls):
        return cls._root_created

    @classmethod
    def root_created(cls):
        cls._root_created = True

    @classmethod
    def get_all_visited(cls):
        # print(cls._visited_links_queue)
        return cls._visited_links_queue

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
        cls._visited_links_queue.put(url)

    @classmethod
    def is_queue_empty(cls):
        return cls._visited_links_queue.empty()

    @classmethod
    def _save_needs_update(cls, url):
        cls._needs_update_queue.put(url)

    @classmethod
    def _get_needs_update(cls):
        return cls._needs_update_queue.get()

    @classmethod
    def _is_needs_update_empty(cls):
        return cls._needs_update_queue.empty()
#******** Node function ***************

    @classmethod
    def save_node_item (cls, item):
        cls._node_data_queue.put(item)
        # cls.node_data_queue.append("5")

    @classmethod
    def get_node_data(cls):
        return cls._node_data_queue.get()

    @classmethod
    def node_data_queue_length(cls):
        print("**********QUEUE LENGTH****************\n",
        cls._node_data_queue.qsize())

    @classmethod
    def is_queue_empty(cls):
        return cls._node_data_queue.empty()