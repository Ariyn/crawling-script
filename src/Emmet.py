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

		self.dataSize = 0
		root = parse(self.splitPattern)
		self.root = root
		self.nodes = self.root.travel(format=lambda index, x:[x])
		
		self.reset()
		self.captures = []
		
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
	def Check(self, element, endTag=False, oneline=None):
		filtered = False
		if endTag and element in self.elementHistory:
			x = [(i[0], element.getAttr(i[1])) for i in self.currentNode.captures if self.currentNode.captures]
			for name, value in x:
				if name in x and type(self.currentCapture[name]) != list:
					self.currentCapture[name] = [self.currentCapture[name]]
				elif name not in x:
					self.currentCapture[name] = value
				elif name in self.currentCapture:
					self.currentCapture[name].append(value)

			for i in range(self.elementHistory.index(element), len(self.elementHistory)):
				self.filterHistory.pop(-1)
				self.elementHistory.pop(-1)

			if not self.filterHistory:
				self.reset(succeed=self.currentNodeFiltered)
			else:
				self.currentNode = self.filterHistory[-1]
		else:
			if not self.currentNodeFiltered and self.parentNodeFiltered:
				return False
			try:
				cn = self.traversal()
				filtered = cn.Match(element)
				print(element, filtered, cn)
				if filtered:
					self.currentNodeFiltered = True
					self.parentNodeFiltered = True
					self.currentNode = cn
					self.filterHistory.append(self.currentNode)
					self.elementHistory.append(element)
				else:
					pass
					print("not passed filtered")
					print(element, filtered, cn)
					self.currentNodeFiltered = False
					self.reverseTraversal()
			except StopIteration:
				"""
				this means finally searching done to the end.
				"""
				print("stop iteration")
				print(self.nodes[-1], element)
				print(self.currentNodeFiltered, self.parentNodeFiltered)
				print(self.filterHistory)
				self.reset()
				pass
		return filtered

	def traversal(self):
		if self.index < len(self.nodes)-1:
			self.index += 1
			retVal = self.nodes[self.index]
		else:
			raise StopIteration
		return self.nodes[self.index]

	def __iter__(self):
		return self
	def __next__(self):
		return self.traversal()
	
	def reverseTraversal(self):
		self.index -= 1

	def reset(self, succeed=False):
# 		print("reset!")
		self.filterHistory = []
		self.elementHistory = []
		self.currentNode = self.root
		self.index = 0
		if succeed:
# 			print('succeed!', self.currentCapture)
			self.captures.append(copy(self.currentCapture))
		self.currentCapture = {}
		self.currentNodeFiltered = True
		self.parentNodefiltered = False

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
