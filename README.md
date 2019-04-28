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

<b>run_my_spiders.py:</b>
  <ul><li>This is the main file. It will launch the WaterLinksSpider, as well as spawn separate processes for the get_headers and fill_nodes functions.</li></ul>
  
  <b>WaterLinksSpider.py:</b>
    <ol>
      <li>This class WaterLinksSpider begins by asyncronously requesting the web page at the assigned URL in the "start_urls" variable.           </li> 
      <li>When it receives a response, it parses it with BeautifulSoup to retreive all the URLs contained in that page</li>
      <li> In a loop, it then applies regex patterns to the first URL retreived and it's surrounding text area to find specific language describing water quality, and other water quality related terms.</li> 
      <li>It then assigns that URL a "quality" rating based on the language found, and contructs a URL "item" (class WaterLink) containing various attributes about that URL (URLs,quality, time_stamp etc.), which is then sent to class CreateNodeRelationships in pipelines.py.<li>
      <li>Still in the loop, the spider then sends an asyncronous request to that URL and repeats the process from step one. So at any given momemnt there may be many different requests and responses in transit. </li>
    </ol>
    
  <b>pipelines.py</b>
    <ol>
     <li>This class receives WaterLinks from WaterLinksSpider.py</li>
     <li>It then stores that WaterLink within class SpiderHomeBase in spider_home_base.py</li>
     <li>It extracts the URL of the page the WaterLink was found on, and extracts the URL of the actual WaterLink then checks whether or not they have been visited already.</li> 
      <li> It then creates nodes in the database for each URL with a relationship representing the connection between them, and saves the URLs into class SpiderHomeBase in spider_home_base.py</li>
    </ol>
  
  <b>spider_home_base.py</b>
    <ol>
      <li> The class SpiderHomeBase is in charge of storing all the visited links, as well as the WaterLinks sent from pipelines.py to later be accessed by UpdateLinksSpider.py, fill_nodes.py and pipelines.py.</li>
      <li> It must use a multiprocessing queue and multiprocessing manager to transfer data to the get_headers() and fill_nodes() methods in UpdateLinksSpider.py and fill_nodes.py, respectively, since these methods are running as separate processes.</li>    
    </ol>
  
  <b>fill_nodes.py</b>
    <ol>
      <li>The method fill_nodes() in class FillNodes is run as a separate process. First it checks whether the _node_data_queue in class SpiderHomeBase is empty.</li>
      <li> If it is not empty, it will pop a WaterLink from the queue, find the node with the matching id in the database, and insert all the the WaterLink attributes into that node.</li
      <li> It repeats this process until the _node_data_queue is empty, then waits to check again after a few seconds.</li>
    </ol>
  
  <b>UpdateLinksSpider.py</b> (not fully functional, can only retrieve)
    <ol>
      <li> The class UpdateLinksSpider does not "crawl" in the same sense as the class WaterLinksSpider, because it does not follow links.</li> 
      <li>It retreives already visited URLs from the class SpiderHomeBase then requests the HTTP headers from that URL.</li>
      <li>Then it compares the 'Last-Modified' header (if there is one) to the timestamp of that URL's node in the database.</li> 
      <li>If the 'Last-Modified' date is more recent than the node timestamp data, that URL will be re-processed and updated in the database.</li>
    </ol>

<h3>Quality Metric Explained</h3>
<ol>
  <li> Each URL is assigned a quality modifier number depending on the scrope where the water quality language is found. This modifier multiplies the quality points accrued from finding water quality related language within that scope.</li>
  <li> If the language is found within the scope of the href attribute (the URL), that would indicate that there is the highest chance this URL will lead to a webpage containing more water quality language and related content. Because of this, it is assigned the highest modifier, 2.</li>
  <li> If there is no water quality language found in the href, the scope depth is decreased by one, and the process is repeated in the anchor tag of that href, which has the second highest quality modifier, 1.8.</li>
  <li> The process is continued with the parent of the anchor, then the grandparent of the anchor, which have the third and fourth largest quality modifers, 0.6 and 0.3, respectively.</li>
</ol>
<ul>
  <li> Each water quality related word is worth 1 quality point. So if the words "water", "drinking", and "polluted" were found within the parent scope, the quality rating would be 3*0.6 = 1.8.</li>
  <li> A scope is considered high quality when the word "water" is found within a certain character distance of the word "quality" or similar words such as "condition" or "resources". This will add 10 points to it's quality rating.</li>
 </ul>
      
<h3><b>Future Functionality</b></h3>
<ul>
  <li>Natural language processing for better link quality recognition using Python NLTK.</li>
  <li>Run multiple spiders starting from differnt URLs</li>
  <li>Traversal of JavaScript links using Scrapy Splash.</li>
  <li>The ability to download and parse PDFs, and other text files.</li>
</ul>
  
    
