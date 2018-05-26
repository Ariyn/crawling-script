import re

class State:
	def __init__(self):
		self.transitions = []
	def Match(self, element):
		raise NotImplemented
	def addTransition(self, target):
		self.transitions.append((target.tag, target))

	def Transition(self, element, ignore=[]):
		changed, state = False, self

		for i in self.transitions:
			if (i[0] == element.tag and i[1].Match(element)) or i[0] in ignore:
				changed, state = True, i[1]
				break

		return changed, state

class EmmetNode(State):
	repeatLambda = lambda x: x if not x else x.groupdict()
	dataTokenEXP = "(?:(?:([a-zA-z0-9-_]+)(?:\s*:=\s*([a-zA-z0-9-_]+))?)\s*,?\s*)"
	tagFilterEXP = "(?P<tag>\w+)(?:\[(?P<condition>(.+?:.+?\s*)+)\]|(?P<id>#(\w|\d|-|_)+)|(?P<name>\*(\w|\d|-|_)+)|(?P<class>(?:\.(\w|\d|-|_)+)*)|{(?P<capture>.+?)})"
	fcTokens = ["(", ")", "+", ">", "^", "**"]
	fcTokenEXP = "(\(|\)|\+|\>|\^|\*\*)"
	fcDataTokenEXP = "\{(.+?)\}"
	
	def __init__(self, pattern=None, root=False):
		super(EmmetNode, self).__init__()

		self.root = root
		if root:
			pattern = "root"
		self.pattern, pattern = pattern, pattern.strip()

		f = re.search(self.tagFilterEXP, pattern)
		f = f.groupdict()

		self.f, self.tag = f, f["tag"]
		self.classes = f["class"].split(".")[1:] if f["class"] else []
		self.ids = f["id"].split("#")[1:] if f["id"] else []
		self.names = f["name"].split("*")[1:] if f["name"] else []
		self.conditions = [i.split(":") for i in f["condition"].split(" ")] if f["condition"] else []
# 		if self.conditions:
# 			print("self.conditions = ",self.conditions)

		data = re.search(self.fcDataTokenEXP, pattern)
		data, hasData = data.group(0) if data else "", True if data else False

		self.dataMapping = re.findall(self.dataTokenEXP, data)
		self.children, self.sibling = [], []

	def __str__(self):
		return self.pattern

	def Match(self, element, remove=False, ignore=[]):
		if self.root:
			return False
		
		tag, attrs = element.tag, element.attrs
		filtered = False
		classes = set(element.classes)
		# classes = set([i[1] for i in attrs if i[0] == "class"][0])
		ids = [i[1].strip() for i in attrs if i[0] == "id"]
		names = [i[1].strip() for i in attrs if i[0] == "name"]
		conditions = {
			"id":ids,
			"name":names,
			"class":classes,
			"body":element.data
		}

		if tag == self.tag:
			filtered = True

			# print("matching", element, filtered, self.classes, classes)
			cls = classes | set(self.classes)
			if cls != classes:
				filtered = False

			for i in self.ids:
				if i not in ids:
					filtered = False
					break
			
			for i in self.names:
				if i not in names:
					filtered = False
					break
					
			for i in self.conditions:
				if i[1] != conditions[i[0]]:
					filtered=False
					break
# 				else:
# 					print("here", i[1], conditions[i[0]])
			
		if self.tag in ignore:
# 			print(self.tag)
			filtered = True
	
		return filtered
