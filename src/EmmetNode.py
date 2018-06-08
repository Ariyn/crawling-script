import re
import copy

tagExp = re.compile(r"^([A-Za-z0-9-_]+)(#[A-Za-z0-9-_]+)?(\.[A-Za-z0-9-_]+)*")
conditionExp = re.compile(r"^\[\W*((?:[A-Za-z0-9-_]+\W*:=\W*[A-Za-z0-9-_]+\W*,?)+)\]")
captureExp = re.compile(r"^\{\W*((?:[A-Za-z0-9-_]+\W*:=\W*[A-Za-z0-9-_]+\W*,?)+)\}")
operatorExp = re.compile(r"^(\+|>|\*)")
bracketExp = (re.compile(r"^(\()"), re.compile(r"^(\))"))

allocationExp = re.compile(r"([A-Za-z0-9-_]+)\W*:=\W*((?:\w|-|_)+)")

idExp = re.compile(r"#([A-Za-z0-9-_]+)")
classExp = re.compile(r"\.([A-Za-z0-9-_]+)")

exps = [bracketExp[0], tagExp, conditionExp, captureExp, operatorExp, bracketExp[1]]

class Node:
	def __init__(self, raw, type="oper"):
		self.raw = raw
		self.type = type
		self.condition, self.captures = [], []

	def __repr__(self):
		return self.raw

	def __str__(self):
		return self.__repr__()

class EmmetNode(Node):
	def __init__(self, raw, type="node", isRoot=False):
		super().__init__(raw, type)
		idString, classString = idExp.search(raw), classExp.findall(raw)

		self.id = idString.group(1) if idString else None
		self.classes = classString
		self.tag = re.search(r"^([A-Za-z0-9-_]+)", self.raw).group()

		self.isRoot = isRoot
		self.children = []
		self.condition, self.captures = [], []
		
		self.target = None
		self.searched = False

		self.__parent = None
		self.__level = 0

	def __repr__(self):
		cond = ", ".join(["%s:=%s"%(i) for i in self.condition])
		capt = ", ".join(["%s:=%s"%(i) for i in self.captures])
		return "<{TagName}{IdName}{ClassName}{Condition}>{Capture}".format(
			TagName = self.tag,
			IdName = ' id="%s"'%self.id if self.id else "",
			ClassName = ' class="%s"'%" ".join(self.classes) if self.classes else "",
			Condition=" [%s]"%cond if cond else "",
			Capture=" {%s}"%capt if capt else ""
		)
	
	@property
	def parent(self):
		return self.__parent
	@parent.setter
	def parent(self, parent):
		self.__parent = parent
		self.__level = parent.level+1

	@property
	def level(self):
		return self.__level
	
	@property
	def sibling(self):
		return self.__parent.children if self.__parent else None
	
	def travel(self, index=0, format=lambda index, x:"%s %s\n"%("  "*index, x.__repr__())):
		x = format(index, self)
		for i in self.children:
			x += i.travel(index=index+1, format=format)
		
		return x
	
	def findTerminal(self):
		cTerminal = sum([i.findTerminal() for i in self.children])
		if cTerminal == 0:
			cTerminal += 1
		return cTerminal

	def capture(self, e):
		x = [(i[0], e.parsedAttrs[i[1]]) for i in self.captures if i[1] in e.parsedAttrs]

		
	"""
		does not check attributes match yet
	"""
	def Match(self, element, **kwargs):
		return self.match(element)
	def match(self, element):
		if self.isRoot:
			return False

		tag, attrs = element.tag, element.attrs
		filtered = False
		classes = set(element.classes)
		id = element.id

		conditions = {
			"id":id,
			"class":classes,
			"body":element.data
		}

		if tag == self.tag:
			filtered = True

		if (classes|set(self.classes)) == classes:
			filtered = filtered & True
		else:
			filtered = False

		if self.id == id:
			filtered = filtered & True
		else:
			filtered = False

		return filtered

def splitToken(string):
	cpStr = copy.copy(string)
	tokens = []
	index = 0
	while len(cpStr) != 0:
		index += 1
		for exp in exps:
			s = exp.search(cpStr)
			if s:
				result = s.group(0)
				tokens.append((s, exp))
				cpStr = cpStr[len(s.group(0)):].lstrip()
				continue
	return tokens

def parse(tokens):
	root = EmmetNode("root", isRoot=True)
	stack = [root, Node(">")]
	for result, exp in tokens:
		resultString = result.group()

		if exp == tagExp:
			stack.append(EmmetNode(resultString))
		elif exp == operatorExp or exp in bracketExp:
			stack.append(Node(resultString))
		elif exp == conditionExp:
			stack[-1].condition += allocationExp.findall(resultString)
		elif exp == captureExp:
			stack[-1].captures += allocationExp.findall(resultString)

		if stack[-1].type == "oper":
			oper = stack[-1]
			if oper.raw == ")":
				for i, v in enumerate(stack[::-1]):
					if v.type == "oper" and v.raw == "(":
						stack = stack[:-i-1]+[stack[-i]]
						break
		if stack[-2].type == "oper" and stack[-1].type == "node":
			oper = stack[-2]
			if oper.raw == ">":
				stack[-3].children.append(stack[-1])
				stack[-1].parent = stack[-3]
				stack = stack[:-2]+stack[-1:]
			elif oper.raw == "+":
				stack[-3].parent.children.append(stack[-1])
				stack[-1].parent = stack[-3].parent
				stack = stack[:-2]+stack[-1:]
			elif oper.raw == "*":
				pass
	
	return root
