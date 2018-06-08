import re
from copy import copy
from .EmmetNode import splitToken, parse

class Emmet:
	def __init__(self, scripts, ignore=[]):
		self.stack, self.stackPointer = [], 0
		self.stateMachine = []
		self.scripts = scripts
		self.ignore = ignore

		self.splitPattern = splitToken(scripts)

		self.debug = False
		self.dataSize = 0
		self.root = parse(self.splitPattern)
		self.nodes = self.root.travel(format=lambda index, x:[x])

		self.reset()
		self.captures = []

		self.treeDict = self.makeTreeDict(self.root)
		self.traversalList = []+self.root.children
		self.possibleList = []+self.root.children
		self.check2CurrentNodes = []+self.root.children
		self.check2OpenList = [
			{"lastElement":self.root, "list":[], "searched":False}
		]

	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return "<%s>"%self.scripts

	def printTree(self, root=None, index=0):
		if not root:
			root = self.root
		n = root
		print("\t"*index+str(n))
		for i in root.children:
			self.printTree(root=i, index=index+1)

	def check(self, *args, **kwargs):
		return self.Check(*args, **kwargs)

	"""
	right now
		t1>t2>t3{aa:=bb}>t4
		<t1><t2><t3 bb=""></t3></t2></t1>

	captured
	"""
	def Check(self, element, endTag=False, oneline=None):
		filtered = False

		if endTag and element == self.currentNode.target:
			x = [(i[0], element.getAttr(i[1])) for i in self.currentNode.captures if self.currentNode.captures]
			for name, value in x:
				if name in x and type(self.currentCapture[name]) != list:
					self.currentCapture[name] = [self.currentCapture[name]]
				elif name not in x:
					self.currentCapture[name] = value
				elif name in self.currentCapture:
					self.currentCapture[name].append(value)

			if len(self.filterHistory)+1 == len(self.nodes):
				self.reset(succeed=self.currentNodeFiltered)
			else:
				x = False
				for c in self.currentNode.children:
					x = x or c.searched
				self.currentNode.searched = False or self.currentNode.children != [] or x
				self.currentNode.target = None
				self.currentNode = self.filterHistory[-1]

		else:
			try:
				cn = self.traverse()
				if not cn.searched and cn.Match(element):
					self.currentNodeFiltered = True
					self.parentNodeFiltered = True

					cn.target = element
					cn.searched = True
					self.currentNode = cn

					self.filterHistory.append(self.currentNode)
					self.elementHistory.append(element)
				else:
					self.reverseTraverse()
			except StopIteration:
				"""
				this means finally searching done to the end.
				"""

				# print("stop iteration")
				# print(self.index)
				# print(self.nodes[-1], element)
				# print(self.currentNodeFiltered, self.parentNodeFiltered)
				# print(self.filterHistory)

				self.reset()
				pass
		return filtered

	def checkOpenTag(self, element):
		cn = self.currentEmmetNode
		if cn.match(element):
			return True
		else:
			return False

	def makeTreeDict(self, root, level=0):
		levelDict = {
			level:[root]
		}
		for i in root.children:
			x = self.makeTreeDict(i, level=level+1)
			for k,v in x.items():
				if k not in levelDict:
					levelDict[k] = []
				levelDict[k] += v

		return levelDict

	def traverseTree(self):
		node = self.traversalList.pop(0)
		self.current = node
		if node in self.possibleList:
			self.possibleList.remove(node)
		self.possibleList += node.children
		self.traversalList = node.children+self.traversalList
		return node
	def traverse(self):
		if self.index < len(self.nodes)-1:
			self.index += 1
			retVal = self.nodes[self.index]
		else:
			raise StopIteration
		return self.nodes[self.index]

	def __iter__(self):
		return self
	def __next__(self):
		return self.traverse()

	def reverseTraverse(self):
		self.index -= 1

	def reset(self, succeed=False, capture={}):
		for i in self.nodes:
			i.searched=False
		self.filterHistory = []
		self.elementHistory = []
		self.index = 0
		self.currentNode = self.root
		if succeed:
			self.captures.append(copy(self.currentCapture))
		self.currentCapture = {}
		self.currentNodeFiltered = True
		self.parentNodefiltered = False

	def printTransitions(self):
		# print(self.root, " ".join(["(%s %s)"%(z[0], str(z[1])) for z in self.root.transitions]))
		for i in [i for i in self.stack if hasattr(i, "transitions")]:
			strs = " ".join(["(%s %s)"%(z[0], str(z[1])) for z in i.transitions])
			# print(i, strs)

	def __getattr__(self, key):
		retVal = None
		if hasattr(self.root, key):
			retVal = getattr(self.root, key)
		return retVal
