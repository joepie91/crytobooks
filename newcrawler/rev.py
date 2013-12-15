import string, random

def random_id():
	return "".join(random.choice(string.lowercase + string.uppercase + string.digits) for x in xrange(0, 14))

class RevisionedDict(object):
	def __init__(self, parent=None):
		self.latest_revision = ""
		self.parent = parent
		self.revisions = {}
		self.objects = {}
		
	def __eq__(self, other):
		# This is a tricky one... we need to compare this RevisionedDict against the other thing - which is almost certainly a dict.
		# We'll just compare keys and values.
		try:
			if set(self.keys()) != set(other.keys()):
				return False
		except AttributeError, e:
			return False # Not a dict(-like)
			
		latest_rev = self._get_latest_revision()
		for key, value in other.iteritems():
			if self.objects[latest_rev[key]] != value:
				return False
				
		return True
		
	def __len__(self):
		return len(self._get_latest_revision())
		
	def __getitem__(self, key):
		return self.objects[self._get_latest_revision()[key]]
		
	def __setitem__(self, key, value):
		obj = self._dump_latest_revision()
		obj[key] = value
		self.update(obj)
		
	def __delitem__(self, key):
		obj = self._dump_latest_revision()
		del obj[key]
		self.update(obj)
		
	def __contains__(self, key):
		return (key in self._get_latest_revision())
		
	def keys(self):
		return self._get_latest_revision().keys()
		
	def values(self):
		return [self.objects[id_] for id_ in self._get_latest_revision().values()]
		
	def items(self):
		return [(key, self.objects[id_]) for key, id_ in self._get_latest_revision().items()]
		
	# The below are awful... this really isn't how iterators are supposed to work
		
	def iterkeys(self):
		return iter(self._get_latest_revision().keys())
		
	def itervalues(self):
		return iter([self.objects[id_] for id_ in self._get_latest_revision().values()])
		
	def iteritems(self):
		return iter([(key, self.objects[id_]) for key, id_ in self._get_latest_revision().items()])
		
	# TODO: __iter__, __reversed__
		
	def _add_revision(data):
		object_map = {}
		latest_rev = self._get_latest_revision()
		anything_changed = False
		
		for key in data.keys():
			try:
				try:
					is_dict = isinstance(self.objects[latest_rev[key]][0], RevisionedDict)
				except IndexError, e:
					is_dict = False
					
				if is_dict:
					unchanged = self.objects[latest_rev[key]][0] == data[key]:
				else:
					unchanged = self.objects[latest_rev[key]] == data[key]:
			except KeyError, e:
				# Doesn't exist in last rev, new key
				unchanged = False
				
			if unchanged:
				# Leave as it is
				object_map[key] = latest_rev[key]
			else:
				# New data!
				if isinstance(data[key], dict): # dict, just need to update values
					new_sub_rev = self.objects[latest_rev[key]].update(data[key])
					self.objects[new_id] = (self.objects[latest_rev[key]], new_sub_rev)
				else:
					new_id = random_id()
					self.objects[new_id] = data[key]
					object_map[key] = new_id
				anything_changed = True
				
		if anything_changed:
			new_rev = random_id()
			self.revisions[new_rev] = (self.latest_revision, object_map) # (parent revision, new object map)
			return new_rev
		else:
			return latest_rev
		
	def _get_latest_revision():
		return self.revisions[self.latest_revision]
	
	def _dump_latest_revision():
		obj = {}
		for key, id_ in self._get_latest_revision().iteritems():
			obj[key] = self.objects[id_]
		return obj
	
	def update(data):
		rev_id = self._add_revision(data)
		self.latest_revision = rev_id
		return rev_id
	
	# TODO: compare!

# Problems:
#  - How to handle list diffs? Can't just replace, would still lose data..
#  - Over-engineering? Python already interns primitives, so no point in storing object references rather than just direct revision maps?
#      -> Would still need to pre-process dicts and lists before storage, and compare them...

# Ideas:
#  - Download PDF/EPUB headers and extract metadata from there
