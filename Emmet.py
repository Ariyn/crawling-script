import re
#import this

class State:
	def __init__(self):
		self.transitions = []
	def Match(self, element):
		raise NotImplemented
	def addTransition(self, target):
		self.transitions.append((target.tag, target))

	def Transition(self, element):
		changed, state = False, self

		for i in self.transitions:
			if i[0] == element.tag and i[1].Match(element):
				changed, state = True, i[1]
				break

		return changed, state

class EmmetNode(State):
	repeatLambda = lambda x:x if not x else x.groupdict()
	dataTokenEXP = "(?:(?:([a-zA-z0-9-_]+)(?:\s*:=\s*([a-zA-z0-9-_]+))?)\s*,?\s*)"
	tagFilterEXP = "(?P<tag>\w+)(?:\[(?P<condition>(.+?:.+?\s*)+)\]|(?P<id>#(\w|\d|-|_)+)|(?P<name>\*(\w|\d|-|_)+)|(?P<class>(?:\.(\w|\d|-|_)+)*)|{(?P<capture>.+?)})"

	def __init__(self, pattern=None, root=False):
		super(EmmetNode, self).__init__()

		self.root = root

		if root:
			pattern = "root"
		self.pattern, pattern = pattern, pattern.strip()

		f = re.search(self.tagFilterEXP, pattern)
		f = f.groupdict()
		# print(f)
		self.f, self.tag = f, f["tag"]
		self.classes = f["class"].split(".")[1:] if f["class"] else []
		self.ids = f["id"].split("#")[1:] if f["id"] else []
		self.names = f["name"].split("*")[1:] if f["name"] else []
		self.conditions = [i.split(":") for i in f["condition"].split(" ")] if f["condition"] else []
# 		if self.conditions:
# 			print("self.conditions = ",self.conditions)

		data = re.search(Emmet.fcDataTokenEXP, pattern)
		data, hasData = data.group(0) if data else "", True if data else False

		self.dataMapping = re.findall(self.dataTokenEXP, data)
		self.children, self.sibling = [], []

	def __str__(self):
		return self.pattern

	def Match(self, element, remove=False):
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

		return filtered

class Emmet:
	# firstClassTokens
	fcTokens = ["(", ")", "+", ">", "^", "**"]
	fcTokenEXP = "(\(|\)|\+|\>|\^|\*\*)"
	fcDataTokenEXP = "\{(.+?)\}"

	def __init__(self, pattern):
		self.stack, self.stackPointer = [], 0
		self.stateMachine = []
		self.pattern = pattern

		self.splitPattern = [i for i in re.split(self.fcTokenEXP, pattern) if i]

		self.dataSize = 0
		self.parse(self.splitPattern)
		self.root = EmmetNode(root=True)
		self.root.addTransition(self.stack[0])
		self.currentNode = self.root
		self.filterHistory = [self.root]
		self.elementHistory = []
		self.dataMappingList = []
# 		self.printTree()
		
	def printTree(self):
		tr = self.root.transitions[0][1]
		print(tr, tr.children, tr.sibling)
		print(tr.transitions)
		for i in self.root.children:
			print(i)

	def getNode(self, index, reverse=False):
		searching = 0 <= index < len(self.stack)
		delta = 1 if not reverse else -1
		pop = []

		index -= delta
		while searching:
			delta = 1 if not reverse else -1
			index += delta
			searching = 0 < index < len(self.stack)
			op = self.stack[index]

# 			print(op, index)


			if op in self.fcTokens:
				if op == ")":
					if pop and pop[-1] == "(":
						op = self.stack[index+delta]
						searching = False
						pop.pop(-1)
					else:
						pop.append(op)

				elif op == "(":
					if reverse and pop and pop[-1] == ")":
						op = self.stack[index-delta]
						searching = False
						pop.pop(-1)
					else:
						pop.append(op)
				elif op == "**":
					reverse = True
				elif op == "+":
					pass
			else:
				if reverse and pop and pop[-1] == ")":
					pass
				else:
					searching = False

		return op

	def parse(self, pattern):
		self.stack = [EmmetNode(v) if v not in self.fcTokens else v for v in pattern]
# 		self.dataSize = sum([1 for i in self.stack if i.hasData])

		_stack = []
		parents = [self.stack[0]]


		### ) should not pop every list directly
		### + or such things should pop every thing in () when they pop index-1
		for i, v in enumerate(self.stack[1:]):
			if v not in self.fcTokens:
				parents[-1].addTransition(v)
				parents.append(v)
			elif v == "+":
				parents.pop(-1)
			elif v == "(":
				_stack.append((len(parents), v))
			elif v == ")":
				for j in _stack[::-1]:
					if j[1] == "(":
						break

				# if self.stack[i+1] == "**":
				x = parents[-1]

				d = []
				for r in range(0, len(parents)-j[0]):
					d.append(parents.pop(-1))

				parents.append(d)
				# print("popping", [str(i) for i in parents])


				# print([str(i) for i in parents], i, len(self.stack), self.stack[i+2])

				if i+2 < len(self.stack) and self.stack[i+2] == "**":
					x.addTransition(parents[-2])
					parents.pop(-1)
					# i+=2
			# elif v == "**":
			# 	parents[-1].addTransition(parents[-2])

	def Check(self, element, endTag=False, oneline=None):
		if endTag and element in self.elementHistory:
			x = [(i[0], element.getAttr(i[1])) for i in self.currentNode.dataMapping if self.currentNode.dataMapping]
			if x:
				self.dataMappingList.append(x)

			for i in range(self.elementHistory.index(element), len(self.elementHistory)):
				self.filterHistory.pop(-1)
				self.elementHistory.pop(-1)

			if not self.filterHistory:
				self.reset()
			else:
				self.currentNode = self.filterHistory[-1]
		else:
			changed, cn = self.currentNode.Transition(element)
			filtered = cn.Match(element)
# 			if element.tag in ["img"]:
# 				print(element, changed, cn, cn.tag, cn.Match(element), cn.classes, filtered)

			if changed and filtered:
				self.currentNode = cn
				# print("start", self.currentNode, element)
				self.filterHistory.append(self.currentNode)
				self.elementHistory.append(element)

	def reset(self):
		print("reset!")
		self.filterHistory = []
		self.elementHistory = []
		self.currentNode = self.root

	def printTransitions(self):
		print(self.root, " ".join(["(%s %s)"%(z[0], str(z[1])) for z in self.root.transitions]))
		for i in [i for i in self.stack if hasattr(i, "transitions")]:
			strs = " ".join(["(%s %s)"%(z[0], str(z[1])) for z in i.transitions])
			print(i, strs)

	def __getattr__(self, key):
		retVal = None
		if hasattr(self.root, key):
			retVal = getattr(self.root, key)
		return retVal

# a = EmmetNode(None, "div#1")
# b = EmmetNode(None, "div#1")
# c = EmmetNode(None, "span#3")

# a.addTransition("div", b)
# b.addTransition("span", c)


# e = Emmet("div#bo_v_con>(img{url:=src}+a)**")
# e.Check(Element("div", [("id", "bo_v_con")]))
# e.Check(Element("img", [("url", "test url")]))
# e.Check(Element("img", [("url", "test url")]), endTag = True)

# # e.printTransitions()
# # print([str(i) for i in e.stack])
# exit(3)
