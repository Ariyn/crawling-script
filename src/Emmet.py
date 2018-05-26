import re
from .EmmetNode import splitToken, parse

class Emmet:
	def __init__(self, scripts, ignore=[]):
		self.stack, self.stackPointer = [], 0
		self.stateMachine = []
		self.scripts = scripts
		self.ignore = ignore

		self.splitPattern = splitToken(scripts)

		self.dataSize = 0
# 		self.parse(self.splitPattern)
		root = parse(self.splitPattern)
		self.root = root

		self.currentNode = self.root
		self.filterHistory = [self.root]
		self.elementHistory = []
		self.dataMappingList = []
		self.captures = []

		self.g = self.recursiveTraversal()
# 		self.printTree()

	def printTree(self, root=None, index=0):
		if not root:
			root = self.root
		n = root
		print("\t"*index+str(n))
		for i in root.children:
			self.printTree(root=i, index=index+1)

	def Check(self, element, endTag=False, oneline=None):
		if endTag and element in self.elementHistory:
			x = [(i[0], element.getAttr(i[1])) for i in self.currentNode.dataMapping if self.currentNode.dataMapping]
			if x:
				self.dataMappingList.append(x)
# 				for name, value in x:
# 					if name in x and type(self.currentCapture[name]) != list:
# 						self.currentCapture[name] = [self.currentCapture[name]]
# 					elif name not in x:
# 						self.currentCapture[name] = value
# 					elif name in self.currentCapture:
# 						self.currentCapture[name].append(value)

			for i in range(self.elementHistory.index(element), len(self.elementHistory)):
				self.filterHistory.pop(-1)
				self.elementHistory.pop(-1)

			if not self.filterHistory:
				self.reset()
			else:
				self.currentNode = self.filterHistory[-1]
		else:
			"""
			this transition could be changed to yield tree traversal.
			when interpreter run this line
			next tree traversal goes on one by one.
			but should i remove transition concept??
			it could be usefull for complex scripting.
			but it's not orthogonal method.
			"""
			changed, cn = self.currentNode.Transition(element, ignore=self.ignore)
			filtered = cn.Match(element, ignore=self.ignore)
			if changed and filtered:
				self.currentNode = cn
				self.filterHistory.append(self.currentNode)
				self.elementHistory.append(element)

	def traversal(self):
		try:
			e = self.g.__next__()
		except StopIteration:
			e = None
		return e

	def recursiveTraversal(self, node=None):
		if not node:
			cn = self.currentNode
		else:
			cn = node

		yield cn
		for n in cn.children:
			yield from self.recursiveTraversal(node=n)

	def reset(self):
		print("reset!")
		self.filterHistory = []
		self.elementHistory = []
		self.currentNode = self.root
		self.currentCapture = {}
		self.g = self.recursiveTraversal()

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
