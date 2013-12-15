import requests, lxml.html, urlparse, time

sess = requests.Session()
sess.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.92 Safari/535.2"})

base_uri = "http://www.google.com/search?gcx=c&sourceid=chrome&ie=UTF-8&q=intitle%3A%22calibre+library%22+inurl%3A%22browse%22"

uri = base_uri

all_results = []

while True:
	response = sess.get(uri)
	xml = lxml.html.fromstring(response.text)
	
	results = xml.xpath("//h3[@class='r']/a/@href")
	next_ = xml.xpath("//a[@id='pnnext']/@href")
	
	for result in results:
		all_results.append(result)
	
	if len(next_) > 0:
		uri = urlparse.urljoin(uri, next_[0])
	else:
		break
		
	time.sleep(1)
	
unique_results = []
	
for result in all_results:
	print "Testing %s..." % result
	try:
		response = requests.get(result, timeout=10)
	except requests.exceptions.RequestException, e:
		# Dead, skip
		continue
	except socket.timeout, e:
		# Also dead, this might be thrown instead of above (see https://github.com/kennethreitz/requests/issues/1797)
		continue
	
	if "Donate to support the development of calibre" not in response.text:
		# Fake...
		continue
	
	# Find base URI for this Calibre
	xml = lxml.html.fromstring(response.text.encode("utf-8"))

	try:
		base_path = xml.xpath("//div[@id='header']//div[@class='bubble']//a/@href")[0]
	except IndexError, e:
		# Not found... probably not a Calibre, just a very good fake?
		continue
		
	result = urlparse.urljoin(result, base_path).rstrip("/")
	
	if result.endswith("/browse"):
		result = result[:-7]
		
	if result not in unique_results:
		print result
		unique_results.append(result)
		
for result in unique_results:
	pass#print result
