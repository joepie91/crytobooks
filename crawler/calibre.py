#!/usr/bin/python
import os, time, sys, urllib, urllib2, threading, re
from collections import deque
from BeautifulSoup import BeautifulSoup

try:
	import json
except:
	import simplejson as json

STOP = False

pipe_name = 'pipe_books'

calibre_urls = deque([])

def add_book(title, authors, description, thumbnail, urls):
	global pipe_name
	
	print "[libcal] Submitted %s" % title
	
	pipeout = os.open(pipe_name, os.O_WRONLY)
	os.write(pipeout, json.dumps({
		'type': "add",
		'data': {
			'title': title,
			'authors': authors,
			'description': description,
			'thumbnail': thumbnail,
			'urls': urls
		}
	}) + "\n")
	os.close(pipeout)
	

class GoogleCrawler (threading.Thread):
	def run(self):
		self.current_start = 0
		self.crawl_page(self.base_url)
	
	def crawl_page(self, url):
		global calibre_urls, STOP
		
		if STOP == True:
			return None
		
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.92 Safari/535.2")]
		response = opener.open(url)
		page_contents = response.read()
		
		print "[google] == FIND CALIBRE LINKS"
		soup = BeautifulSoup(page_contents)
		for subsoup in soup.findAll("li", "g"):
			url = subsoup.find("a", "l")['href']
			url_matcher = re.compile("(https?:\/\/[^/]*.*\/)browse\/.*")
			
			try:
				url = url_matcher.match(url).group(1)
			except AttributeError:
				continue
				
			if url not in calibre_urls:
				print "[google] Found Calibre at %s" % url
				calibre_urls.append(url)
				
		print "[google] == FIND NEXT PAGE"
		next_url = ""
		subsoup = soup.find("table", attrs={'id':'nav'})
		for item in subsoup.findAll("a", "fl"):
			new_start = int(re.search("start=([0-9]+)", item['href']).group(1))
			if new_start == self.current_start + 10:
				self.current_start = new_start
				next_url = item['href']
				
		if next_url == "":
			print "[google] No next pages found... Done spidering Google!"
		else:
			
			print "[google] == SLEEPING..."
			time.sleep(4)
			#self.crawl_page("http://www.google.com" + next_url)

class CalibreCrawler(threading.Thread):
	def run(self):
		global calibre_urls, STOP
		
		while STOP == False:
			if len(calibre_urls) > 0:
				current_url = calibre_urls.popleft()
				self.crawl_page(current_url)
				
			time.sleep(1)
	
	def crawl_page(self, url):
		url_matcher = re.compile("(https?:\/\/[^/]*).*")
		base = url_matcher.match(url).group(1)

		print "[calibr] Starting crawl on %s ..." % url

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
						
						final_urls = []
						
						for format_url in urls:
							url_matcher = re.compile(".*\/get\/([^/]+)\/.*")
							m = url_matcher.match(format_url)
							filetype = m.group(1).lower()
							download_url = base + format_url
							final_urls.append({
								'filetype': filetype,
								'url': download_url
							})
							
						add_book(title, authors, description, thumbnail, final_urls)
					
					except Exception, e:
						print "[calibr] FAILED: '%s' by '%s', error: %s" % (title, authors, str(e))
						
				time.sleep(2)
			except:
				pass

try:
	google = GoogleCrawler()
	google.base_url = "http://www.google.com/search?gcx=c&sourceid=chrome&ie=UTF-8&q=intitle%3A%22calibre+library%22+inurl%3A%22browse%22"
	google.start()
	
	calibre = CalibreCrawler()
	calibre.start()
except KeyboardInterrupt:
	STOP = True
