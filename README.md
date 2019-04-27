# Water-Links-Scraper

<p>Water-Links-Scraper is a web crawler designed to start from a root web page, 
retreive all the hyperlinks, and analyze which links are more related to content 
regarding water quality, and related water quality topics. All links will be assigned a content rating and inserted into the graph database, Neo4j, their connections to eachother can be stored as relationships. 

<h3> Installing Scrapy </h3>
<p>Follow <a href='http://doc.scrapy.org/en/latest/intro/install.html'> these instructions </a>to install Scrapy.</p>
<p>It is reccommended to follow the virtual environment install option.</p>

<h3> Installing Neo4j </h3>
<p>Follow <a href='https://neo4j.com/docs/operations-manual/current/installation/'>these instructions </a> to install Neo4j. Once you've opened the Neo4j browser, create a new user with the credentials listed at the bottom of the <b>settings.py</b>  file.</p>

<h3> Dependencies </h3>
<ul>
  <li><a href='https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup'>BeautifulSoup4</a>(for page parsing)</li>
  <li><a href='https://pypi.org/project/certifi/'>certifi </a>(SSL for getting headers)</li>
  <li><a href='https://pypi.org/project/urllib3/'>urllib3 </a>(for getting headers)</li>
  <li><a href='https://github.com/neo4j-contrib/neovis.js/'>Neovis.js </a>(for visualize.html)</li>
 </ul>
  

<p>Clone this repository into your virtual environment, and make sure it is activated
by running the command:</p>
<p><b>$: source ~/virtual_workspace/bin/activate</b></p>
<p>then</p>
<p><b>$: python run_my_spiders.py</b></p>

<h3>Overview of Design</h3>
<ul>
  <li><b>run_my_spiders.py:</b></li>
  <ul><li>This is the main file. It will launch the WaterLinksSpider, as well as spawn separate processes for the get_headers and fill_nodes functions.</li></ul>
  <li><b>WaterLinksSpider.py:</b></li>
    <ol>
      <li>This class WaterLinksSpider begins by asyncronously requesting the web page at the assigned URL in the "start_urls" variable.           </li> 
      <li>When it receives a response, it parses it with BeautifulSoup to retreive all the URLs contained in that page</li>
      <li> In a loop, it then applies regex patterns to the first URL retreived and it's surrounding text area to find specific language describing water quality, and other water quality related terms.</li> 
      <li>It then assigns that URL a "quality" rating based on the language found, and contructs a URL "item" (class WaterLink) containing various attributes about that URL (URLs,quality, time_stamp etc.), which is then sent to class CreateNodeRelationships in pipelines.py.<li>
      <li>Still in the loop, the spider then sends an asyncronous request to that URL and repeats the process from step one. So at any given momemnt there may be many different requests and responses in transit. </li>
    </ol>
    
  <li><b>pipelines.py</b></li>
    <ol>
     <li>This class receives WaterLinks from WaterLinksSpider.py</li>
     <li>It then stores that WaterLink within class SpiderHomeBase in spider_home_base.py</li>
     <li>It extracts the URL of the page the WaterLink was found on, and extracts the URL of the actual WaterLink then checks whether or not they have been visited already.</li> 
      <li> It then creates nodes in the database for each URL with a relationship representing the connection between them, and saves the URLs into class SpiderHomeBase in spider_home_base.py</li>
    </ol>
  
  <li><b>spider_home_base.py</b></li>
    <ol>
      <li> The class SpiderHomeBase is in charge of storing all the visited links, as well as the WaterLinks sent from pipelines.py to later be accessed by UpdateLinksSpider.py, fill_nodes.py and pipelines.py.</li>
      <li> It must use a multiprocessing queue and multiprocessing manager to transfer data to the get_headers() and fill_nodes() methods in UpdateLinksSpider.py and fill_nodes.py, respectively, since these methods are running as separate processes.</li>    
    </ol>
  
  <li><b>fill_nodes.py</b></li>
    <ol>
      <li>The method fill_nodes() in class FillNodes is run as a separate process. First it checks whether the _node_data_queue in class SpiderHomeBase is empty.</li>
      <li> If it is not empty, it will pop a WaterLink from the queue, find the node with the matching id in the database, and insert all the the WaterLink attributes into that node.</li
      <li> It repeats this process until the _node_data_queue is empty, then waits to check again after a few seconds.</li>
    </ol>
  
  <li><b>UpdateLinksSpider.py</b> (not fully functional, can only retrieve)</li>
    <ol>
      <li> The class UpdateLinksSpider does not "crawl" in the same sense as the class WaterLinksSpider, because it does not follow links.</li> 
      <li>It retreives already visited URLs from the class SpiderHomeBase then requests the HTTP headers from that URL.</li>
      <li>Then it compares the 'Last-Modified' header (if there is one) to the timestamp of that URL's node in the database.</li> 
      <li>If the 'Last-Modified' date is more recent than the node timestamp data, that URL will will be re-processed and updated in the database.</li>
    </ol>
</ul>
      

