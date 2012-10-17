#!/usr/bin/python
import os, time, sys, json, _mysql

def stringdammit(input_string):
	if isinstance(input_string, str):
		return input_string
	else:
		return input_string.encode('utf-8')

config = json.load(open("config.json"))
db = _mysql.connect(config['host'], config['user'], config['password'], config['database'])

pipe_name = 'pipe_books'

if not os.path.exists(pipe_name):
	os.mkfifo(pipe_name)

pipein = open(pipe_name, 'r')
buff = ""

while True:
	data = pipein.read()
	buff += data
	stack = buff.replace("\r", "").split("\n")
	buff = stack.pop()
	
	for line in stack:
		try:
			obj = json.loads(line)
		except:
			print line
			sys.stderr.write("ERROR: Could not decode message: %s" % line)
			continue
		
		message_type = obj['type']
		message_data = obj['data']
		
		if message_type == "add":
			s_title = db.escape_string(stringdammit(message_data['title']))
			s_description = db.escape_string(stringdammit(message_data['description']))
			s_authors = db.escape_string(stringdammit(message_data['authors']))
			s_thumbnail = db.escape_string(stringdammit(message_data['thumbnail']))
			
			sql_query = "SELECT * FROM books WHERE `Thumbnail` = '%s'" % s_thumbnail
			db.query(sql_query)
			sql_result = db.store_result()
			
			if sql_result.num_rows() == 0:
				sql_query = "INSERT INTO books (`Title`, `Authors`, `Description`, `Thumbnail`) VALUES ('%s', '%s', '%s', '%s')" % (s_title, s_authors, s_description, s_thumbnail)
				db.query(sql_query)
				book_id = db.insert_id()
				
				for format_url in message_data['urls']:
					s_filetype = db.escape_string(stringdammit(format_url['filetype'].lower()))
					s_url = db.escape_string(stringdammit(format_url['url']))
					
					sql_query = "INSERT INTO files (`BookId`, `Format`, `Url`) VALUES ('%d', '%s', '%s')" % (book_id, s_filetype, s_url)
					db.query(sql_query)
					
				print "Received and inserted '%s' by '%s'" % (s_title, s_authors)
			else:
				print "Skipped '%s' by '%s' (already exists)" % (s_title, s_authors)
		else:
			print "Unrecognized command: %s" % message_type
