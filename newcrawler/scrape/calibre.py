import lxml.html, requests, urlparse, re
from lxml import etree
from datetime import datetime

endpoint = "http://caltsardragon.com:8080"

def get_date(string):
	# Because for whatever reason, strptime doesn't work
	month, year = string.split()
	month_map = {
		"Jan": 1,
		"Feb": 2,
		"Mar": 3,
		"Apr": 4,
		"May": 5,
		"Jun": 6,
		"Jul": 7,
		"Aug": 8,
		"Sep": 9,
		"Oct": 10,
		"Nov": 11,
		"Dec": 12
	}
	
	return (int(year), month_map[month])

	
# We'll retrieve a list of all book IDs for this installation
response = requests.get("%s/browse/category/allbooks" % endpoint)
xml = lxml.html.fromstring(response.text.encode("utf-8"))
book_ids = {}

for item in xml.xpath("//*[@id='booklist']/div[@class='page']/div[@class='load_data']/@title"):
	response = requests.post("%s/browse/booklist_page" % endpoint, data={"ids": item})
	xml_titles = lxml.html.fromstring(response.json().encode("utf-8"))
	title_map = {}
	
	for subitem in xml_titles.xpath("//div[@class='summary']"):
		#print str(etree.tostring(subitem))
		id_ = subitem.xpath("div[@class='details-href']/@title")[0].split("/")[-1]
		title = subitem.xpath("div/div[@class='title']/strong/text()")
		book_ids[id_] = title
	print "Done %s..." % item

for id_, title in book_ids.iteritems():
	details_url = "/browse/details/%s" % id_
	cover_url = "/get/cover/%s" % id_
	
	response = requests.get(endpoint + details_url)
	xml = lxml.html.fromstring(response.json().encode("utf-8"))
	#print etree.tostring(xml)
	
	downloads = {}
	
	for item in xml.xpath("//div[@class='field formats']/a"):
		filetype = item.get("title")
		url = endpoint + item.get("href")
		downloads[filetype.lower()] = url
		
	isbn = xml.xpath("//div[@class='field']/a[starts-with(@title,'isbn:')]/text()")
	amazon = xml.xpath("//div[@class='field']/a[starts-with(@title,'amazon:')]/@href")
	google = xml.xpath("//div[@class='field']/a[starts-with(@title,'google:')]/@href")
	
	tags = xml.xpath("//div[@class='field']/a[starts-with(@title,'Browse books by tags:')]/text()")
	publish_date = [get_date(date) for date in xml.xpath("//div[@class='field' and strong/text() = 'Published: ']/text()")]
	language = xml.xpath("//div[@class='field' and strong/text() = 'Languages: ']/text()")
	publishers = xml.xpath("//div[@class='field']/a[starts-with(@title,'Browse books by publisher:')]/text()")
	authors = xml.xpath("//div[@class='field']/a[starts-with(@title,'Browse books by authors:')]/text()")
	
	series = xml.xpath("//div[@class='field']/a[starts-with(@title,'Browse books by series:')]/text()")
	if len(series) > 0:
		try:
			series_title, series_id = re.match("(.+) \[(.+)\]$", series[0]).groups(1)
		except AttributeError, e:
			series_title, series_id = (None, None)
	else:
		series_title, series_id = (None, None)
		
	print "%s: %s" % (series_title, series_id)
	
	obj = {
		"ids": {
			"isbn": isbn,
			"amazon": amazon,
			"google": google,
		},
		"title": title,
		"authors": authors,
		"publishers": publishers,
		"publish_date": publish_date,
		"language": language,
		"tags": tags,
		"urls": downloads,
		"cover_url": cover_url,
		"series": [
			{
				"title": series_title,
				"item": series_id
			}
		]
	}
	
	print obj
