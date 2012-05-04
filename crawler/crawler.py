import urllib, urllib2, re, _mysql, time, math, threading, htmlentitydefs
from collections import deque
from BeautifulSoup import BeautifulSoup

# Don't forget to configure the database login at the bottom of the code!

class GoogleCrawler (threading.Thread):
	def run(self):
		google_start()
		
class CalibreCrawler (threading.Thread):
	def run(self):
		calibre_loop()

def crawl_page(url):
	try:
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.92 Safari/535.2")]
		response = opener.open(url)
		page_contents = response.read()
		find_links(page_contents)
		time.sleep(4)
		next_url = find_next(page_contents)
		if next_url == "":
			print "Done."
		else:
			crawl_page("http://www.google.com" + next_url)
	except:
		crawl_page(url)

def find_links(page):
	soup = BeautifulSoup(page)
	for subsoup in soup.findAll("li", "g"):
		url = subsoup.find("a", "l")['href']
		url_matcher = re.compile("(https?:\/\/[^/]*.*\/)browse\/.*")
		url = url_matcher.match(url).group(1)
		if url not in calibre_urls:
			print url
			calibre_urls.append(url)

def find_next(page):
	global current_start
	soup = BeautifulSoup(page)
	subsoup = soup.find("table", attrs={'id':'nav'})
	for item in subsoup.findAll("a", "pn"):
		new_start = find_start(item['href'])
		if new_start == current_start + 10:
			current_start = new_start
			return item['href']
	return ""

def find_start(url):
	url_match = re.search("start=([0-9]+)", url)
	if url_match is None:
		return 0
	else:
		return int(url_match.group(1))
		
def google_start():
	crawl_page(base_url)
	
def calibre_crawl(url):
	try:
		url_matcher = re.compile("(https?:\/\/[^/]*).*")
		base = url_matcher.match(url).group(1)

		print "Starting crawl on %s ..." % url

		response = urllib2.urlopen(url + "browse/category/allbooks")
		page_contents = response.read()

		matcher = re.compile("<div class=\"load_data\" title=\"([\[\]0-9\s,]*)\">")

		for result in matcher.finditer(page_contents):
			try:
				query = result.group(1)
				
				list_url = url + "browse/booklist_page"
				data = urllib.urlencode({'ids': query})
				req = urllib2.Request(list_url, data)
				response = urllib2.urlopen(req)
				page_contents = response.read()[1:-1].replace("\\n", "").replace("\\\"", "\"")

				soup = BeautifulSoup(page_contents)
				
				for subsoup in soup.findAll("div", "summary"):
					try:
						title = subsoup.find("div", "title").strong.string
						authors = subsoup.find("div", "authors").string
						description = subsoup.find("div", "comments").prettify()
						
						try:
							thumbnail = base + subsoup.find("div", "left").img['src']
						except:
							thumbnail = ""
						
						urls = []
						urls.append(subsoup.find("a", "read")['href'])
						
						formats_list = subsoup.find("div", "formats")
						for format_url in formats_list.findAll("a"):
							urls.append(format_url['href'])
						
						s_title = db.escape_string(title)
						s_authors = db.escape_string(authors)
						s_description = db.escape_string(description)
						s_thumbnail = db.escape_string(thumbnail)
						
						sql_query = "SELECT * FROM books WHERE `Thumbnail` = '%s'" % s_thumbnail
						db.query(sql_query)
						sql_result = db.store_result()
						
						if sql_result.num_rows() == 0:
							sql_query = "INSERT INTO books (`Title`, `Authors`, `Description`, `Thumbnail`) VALUES ('%s', '%s', '%s', '%s')" % (s_title, s_authors, s_description, s_thumbnail)
							#print sql_query
							
							db.query(sql_query)
							ins_id = db.insert_id()
							
							for format_url in urls:
								url_matcher = re.compile(".*\/get\/([^/]+)\/.*")
								m = url_matcher.match(format_url)
								filetype = m.group(1).lower()
								download_url = db.escape_string(base + format_url)
								
								s_filetype = db.escape_string(filetype)
								s_url = db.escape_string(download_url)
								
								sql_query = "INSERT INTO files (`BookId`, `Format`, `Url`) VALUES ('%d', '%s', '%s')" % (ins_id, s_filetype, s_url)
								db.query(sql_query)
								
							print "SUCCESS: %s" % s_title
						else:
							print "SKIP: %s" % title
							
						time.sleep(0.1)
					
					except:
						print "FAIL: %s" % title
						
				time.sleep(2)
			except:
				pass
	except:
		pass

def calibre_loop():
	global calibre_urls
	while True:
		if len(calibre_urls) > 0:
			current_url = calibre_urls.popleft()
			calibre_crawl(current_url)
		time.sleep(1)

calibre_urls = deque([])
current_start = 0
base_url = "http://www.google.com/search?gcx=c&sourceid=chrome&ie=UTF-8&q=intitle%3A%22calibre+library%22+inurl%3A%22browse%22"
db = _mysql.connect("localhost", "root", "", "ebooks")

GoogleCrawler().start()
CalibreCrawler().start()