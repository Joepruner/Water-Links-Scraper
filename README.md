# Water-Links-Scraper

<p>Water-Links-Scraper is a web crawler designed to start from a root web page, 
retreive all the hyperlinks, and analyze which links are more related to content 
regarding water quality, and related water quality topics. All links will be assigned a content rating and inserted into the graph database, Neo4j, their connections to eachother can be stored as relationships. 

<h3> Installing Scrapy </h3>
<p>Follow the instructions on <a href='http://doc.scrapy.org/en/latest/intro/install.html'>this page</a> to install Scrapy. It is reccommended to follow the virtual environment install option.</p>

<h3> Installing Neo4j </h3>
<p>Follow the instruction on <a href='https://neo4j.com/docs/operations-manual/current/installation/'> to install Neo4j.</a></p>

<h3> Dependencies </h3>
<ul>
  <li><a href='https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup'>BeautifulSoup4</a>(for page parsing)</li>
  <li><a href='https://pypi.org/project/certifi/'>certifi </a>(SSL for getting headers)</li>
  <li><a href='https://pypi.org/project/urllib3/'>urllib3 </a>(for getting headers)</li>
  <li><a href='https://github.com/neo4j-contrib/neovis.js/'>Neovis.js </a>(for visualize.html)</li>
  

<p>Clone this repository into your virtual environment, and make sure it is activated
by running the command:</p>
<p><b>$: source ~virtual_workspace/bin/activate</b></p>
<p>then</p>
<p>$: python run_my_spiders.py </p>

