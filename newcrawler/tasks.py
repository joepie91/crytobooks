import uuid, os, json, shutil, re
from collections import defaultdict, deque

class TaskManager(object):
	def __init__(self):
		self.tasks = {}
		
	def get(self, task_id):
		return self.tasks[task_id]
		
	def put(self, task_id, task_data):
		# Persist on disk
		try:
			os.mkdirs("task_data/%s" % task_id)
		except OSError, e:
			pass
			
		with open("task_data", "w") as task_file:
			task_file.write(json.dumps(task_data))
			
		# Store in RAM
		self.tasks[task_id] = task_data
		
	def delete(self, task_id):
		shutil.rmtree("task_data/%s" % task_id, ignore_errors=True)
		del self[task_id]
	
class TaskDistributor(object):
	def __init__(self):
		self.pools = defaultdict(deque)
		self.processing = defaultdict(list)
		
	def put(self, pool, task_id):
		self.pools[pool].append(task_id)
		
	def get(self, pool):
		task_id = self.pools[pool].popleft()
		self.processing[pool].append(task_id)
		return task_id
		
	def get_pools(self, task_id):
		return [pool in self.pools if task_id in pool]
		
	def done(self, pool, task_id):
		self.processing[pool].remove(task_id)
		
	def fail(self, pool, task_id):
		# Re-add
		self.processing[pool].remove(task_id)
		self.put(pool, task_id)

class IsbnProcessor(object):
	def clean(self, isbn):
		isbn = isbn.upper().replace("-", "").replace(" ", "")
		
		if len(isbn) == 9: # 9 digit SBN
			isbn = "0" + isbn
			
		return isbn
		
	def validate(self, isbn):
		isbn = self.clean(isbn)
		
		if len(isbn) == 10:
			total = 0
			for i in xrange(0, 9):
				total += (int(isbn[i]) * (10 - i))
			
			check_digit = 11 - (total % 11)
			if check_digit == 10:
				check_digit = "X"
			else:
				check_digit = str(check_digit)
				
			return (check_digit == isbn[9])
		elif len(isbn) == 13:
			odd = False
			total = 0
			for i in xrange(0, 12):
				if odd:
					total += int(isbn[i])
				else:
					total += int(isbn[i]) * 3
				odd = not odd
			
			check_digit = 10 - (total % 10)
			if check_digit == 10:
				check_digit = 0
			check_digit = str(check_digit)
			
			return (check_digit == isbn[12])
		else:
			return False

class BookTaskClassifier(object):
	def __init__(self):
		self.isbn = IsbnProcessor()
		
	def get_pools(self, task_data):
		eligible_pools = []
		
		try:
			for isbn in [isbn.strip() for isbn in task_data["book_data"]["ids"]["isbn"]]:
				if self.isbn.validate(isbn) and "isbn" not in task_data["pools_done"]:
					eligible_pools.append("isbn")
		except KeyError, e:
			pass
			
		for identifier in ("amazon", "google"):
			try:
				if task_data["book_data"]["ids"][identifier].strip() != "" and identifier not in task_data["pools_done"]:
					eligible_pools.append(identifier)
			except KeyError, e:
				pass
				
		if len(eligible_pools) == 0 and "title" not in task_data["pools_done"]:
			eligible_pools.append("title")
				
		return eligible_pools

class BookTaskManager(object):
	def __init__(self):
		self.manager = TaskManager()
		self.distributor = TaskDistributor()
		self.classifier = BookTaskClassifier()
		
	def new(self, book_data):
		task_id = uuid.uuid4()
		task_data = {
			"id": task_id,
			"book_data": book_data,
			"pools_done": [],
			"logs": [],
			"flags": []
		}
		
		self.manager.put(task_id, task_data)
		self.enqueue(task_id)
		
	def enqueue(self, task_id):
		task_data = self.manager.get(task_id)
		pools = self.classifier.get_pools(task_data)
		
		if len(pools) > 1:
			for pool in pools:
				self.distributor.put(pool, task_id)
		else:
			# No more pools to put this into... this is the best we have!
			
	def get(self, pool):
		task_id = self.distributor.get(pool)
		return task_id
			
	def done(self, pool, task_data):
		self.distributor.done(pool, task_data["id"])
		self.manager.put(task_data["id"], task_data) # conflicts..
