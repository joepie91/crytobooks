import requests, re

source = "http://www.loc.gov/z3950/gateway.html"

for match in re.findall('"http:\/\/www\.loc\.gov\/cgi-bin\/zgstart\?ACTION=INIT&FORM_HOST_PORT=\/prod\/www\/data\/z3950\/.+\.html,([^,]+),([0-9]+)"', requests.get(source).text):
	host, port = match
	print "%s:%s" % (host, port)
