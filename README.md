# Water-Links-Scraper

<p>Water-Links-Scraper is a web crawler designed to start from a root web page, 
retreive all the hyperlinks, and analyze which links are more related to content 
regarding water quality, and related water quality topics. All links will be assigned a content rating and inserted into the graph database, Neo4j, their connections to eachother can be stored as relationships. 

<h3> Installing Scrapy </h3>
<p>Follow <a href='http://doc.scrapy.org/en/latest/intro/install.html'> these instructions </a>to install Scrapy.</p>
<p>It is reccommended to follow the virtual environment install option.</p>

<h3> Installing Neo4j </h3>
<p>Follow <a href='https://neo4j.com/docs/operations-manual/current/installation/'>these instructions </a> to install Neo4j. Once you've opened the Neo4j browser, create a new user with the credentials listed at the bottom of the "settings.py"  file.</p>

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
  <li><b>run_my_spiders.py:</b> This is the main class. It will launch the WaterLinksSpider, as well as spawn processes for the get_headers and fill_nodes functions.</li>
  <li><b>WaterLinksSpider.py:</b> 
    <ol>
      <li>This spider begins by requesting the web page at the assigned URL in the "start_urls" variable.</li> 
      <li>When it receives a response, it parses it with BeautifulSoup to retreive all the URLs contained in that page, then applies regex patterns to each URL and it's surrounding text area to find specific language describing water quality, and other water quality related terms.</li> <li>It then assigns each URL a "quality" rating based on the language found, and contructs a URL "item" containing various attributes about that URL, which is then sent to pipelines.py.<li>
      <li>The spider then repeats this process, asyncronously sending requests to all the URLs it has found, then parsing and itemizing the responses.</li>
    </ol>
   
</ul>
      

