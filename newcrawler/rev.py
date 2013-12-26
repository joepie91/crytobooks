# Problems:
#  - How to handle list diffs? Can't just replace, would still lose data..
#  - Over-engineering? Python already interns primitives, so no point in storing object references rather than just direct revision maps?
#      -> Would still need to pre-process dicts and lists before storage, and compare them...

# Ideas:
#  - Download PDF/EPUB headers and extract metadata from there

import string, random, copy
from collections import OrderedDict
from difflib import SequenceMatcher

class RevisionedDict(object):
	def __init__(self, data):
		self._revisions = OrderedDict({})
		self._applied_diffs = []
		self._add_revision(data)
		
	def _generate_revision_id(self):
		return "".join(random.choice(string.lowercase + string.uppercase + string.digits) for x in xrange(0, 14))
	
	def _add_revision(self, data):
		new_revision_id = self._generate_revision_id()
		self._revisions[new_revision_id] = copy.deepcopy(data)
		self._last_revision = new_revision_id
		return new_revision_id
		
	def _get_last_revision(self): # Always returns a copy!
		base_revision = copy.deepcopy(self._revisions[self._last_revision])
		base_revision["_rev"] = self._last_revision # This is to be able to identify the source revision for a modified serialized object later
		return base_revision
		
	def _apply_diff(self, diff):
		new_data = diff.apply(self._get_last_revision(), self._diffs_since(diff.origin_revision))
		new_revision_id = self._add_revision(new_data)
		self._applied_diffs.append((new_revision_id, diff))
		
	def _diffs_since(self, revision_id):
		try:
			revision_index = next(x for x in enumerate(self._applied_diffs) if x[1][0] == revision_id)
			return [x[1] for x in self._applied_diffs[revision_index[0] + 1:]]
		except StopIteration, e:
			return [x[1] for x in self._applied_diffs]
		
	def update(self, data):
		diff = self.autodiff(data)
		self._apply_diff(diff)
			
	def diff(self, data, origin_revision):
		# Figure out if any revisions happened in the meantime
		return RevisionedDictDiff(data, self._revisions[origin_revision], origin_revision)
		
	def autodiff(self, data):
		# Takes the revision number from the data
		return self.diff(data, data["_rev"])
		
class RevisionedDictDiff(object):
	def __init__(self, data, origin_data, origin_revision):
		self.origin_revision = origin_revision
		self._diff_data = self._diff_structure(data, origin_data)
		
	def _diff_structure(self, structure, origin_structure, structure_key=None):
		if isinstance(structure, dict):
			if isinstance(origin_structure, dict):
				# Compare dicts
				opcodes = []
				
				removed_keys = set(origin_structure.keys()) - set(structure.keys())
				
				for key in removed_keys:
					opcodes.append(("delete", key))
				
				new_keys = set(structure.keys()) - set(origin_structure.keys())
				
				for key in new_keys:
					if key != "_rev": # Ignore added _rev key
						opcodes.append(("insert", key, structure[key]))
					
				for key, value in structure.iteritems():
					if key not in new_keys:
						if value == origin_structure[key]:
							opcodes.append(("equal", key))
						else:
							if isinstance(value, dict) or isinstance(value, list):
								opcodes.append(self._diff_structure(value, origin_structure[key], structure_key=key))
							else:
								opcodes.append(("replace", key, value))
				
				return ("dict", structure_key, opcodes)
			else:
				return ("replace", structure)
		elif isinstance(structure, list):
			if isinstance(origin_structure, list):
				# Compare lists (does NOT support nested dictionaries yet!)
				return ("list", structure_key, SequenceMatcher(a=origin_structure, b=structure, autojunk=False).get_opcodes())
			else:
				return ("replace", structure)
		else:
			return ("replace", structure)
			
	def _apply_structure(self, structure, diff_data, intermediate_diffs):
		pass
		# for every key
			# if list
				# calculate_offsets (TODO)
				# apply structure
			# if dict
				# apply structure
			# else
				# apply diff data
		# return key
		
	def apply(data, intermediate_diffs=[]):
		# This will apply the diff against the specified source data
		data = copy.deepcopy(data)
		self._apply_structure(data, self._diff_data, intermediate_diffs)
		
		
		
origin = {
	"type": "message",
	"data": {
		"title": "Sample title",
		"author": "Sample author",
		"isbn": ["a0", "a1", "a2", "a3"],
		"description": ["test one", "test two"],
		"eq": ["a", "b", "c"]
	}
}

"""
revdict = RevisionedDict(origin)
origin = revdict._get_last_revision()

origin["herp"] = "derp"
origin["data"]["isbn"].remove("a2")
origin["data"]["isbn"].insert(0, "a4")
origin["data"]["author"] = "Other author"

#import json
#print json.dumps(revdict.autodiff(origin)._diff_data, indent=4)

revdict.update(origin)

"""

revdict = RevisionedDict(origin)

for i in xrange(0, 5):
	x = revdict._add_revision("blah")
	revdict._applied_diffs.append((x, i))
	
base_rev = revdict._last_revision

for i in xrange(5, 10):
	x = revdict._add_revision("blah")
	revdict._applied_diffs.append((x, i))
		
print revdict._diffs_since(base_rev)
