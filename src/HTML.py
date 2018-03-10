from .Emmet import Emmet

from html.parser import HTMLParser
import re
import sys

class Element:
	MaxRecursive = 2
	def __init__(self, tag, attr = []):
		attr = [(str(i[0]), str(i[1])) for i in attr]

		self.strAttr = [" = ".join(v) if type(v[1]) == str else " = ".join(" ".join(v[1])) for v in attr]

		self.tag, self.attrs = tag, attr
		self.parsedAttrs = {i[0]:i[1] for i in self.attrs}
		self.id = self.parsedAttrs["id"] if "id" in self.parsedAttrs else None
		self.classes = self.parsedAttrs["class"].split(" ") if "class" in self.parsedAttrs else []
		# self.parsedAttrs["class"] = self.parsedAttrs["class"].split(" ")
		# print(self.parsedAttrs)
		self.data, self.children = "", []
		self.parent = None
# 		all-body
	def addChildren(self, child):
		self.children.append(child)
		child.parent = self
		
	def setData(self, data):
		self.data += data.strip()
		self.parsedAttrs["body"] = self.data

	def getAttr(self, key, retVal = None, index=0):
		if key in self.parsedAttrs:
			retVal = self.parsedAttrs[key]
		return retVal

	def __str__(self):
		# print(self.attrs)
		return "<%s %s>%s</%s>"%(self.tag, " ".join(self.strAttr), self.data.replace("\n", "\\n"), self.tag)

	def printTree(self, depth = 0):
		print("%s<%s %s>%s"%("\t"*depth, self.tag, " ".join(self.strAttr), self.data.replace("\n", "\\n")))

		for i in self.children:
			i.printTree(depth+1)

		print("%s</%s>"%("\t"*depth, self.tag))

class MyHTMLParser(HTMLParser):
# 	tagFilterEXP = "(?P<tag>[a-zA-z0-9]+)(?:(?P<id>#[a-zA-z0-9_\-]+)|(?P<class>(?:\.[a-zA-z0-9_\-]+)*)|{(?P<capture>.+?)})"
	onelineTags = ["img", "br"]
	def __init__(self):
		super(MyHTMLParser, self).__init__()
		self.root = Element("Root")
		self.html = ""

		self.parsingTags = [self.root]
		self.tags = [self.root]

		self.emmetEngine = []
		self.parseEncounter = 0

	def handle_startendtag(self, tag, attrs):
		self.handle_starttag(tag, attrs, oneline=True)
		self.handle_endtag(tag, oneline=True)

	def handle_starttag(self, tag, attrs, oneline=False):
		e = Element(tag, attrs)
		[i.Check(e) for i in self.emmetEngine]
			
		self.parsingTags[-1].addChildren(e)
		self.tags.append(e)
		self.parsingTags.append(e)
		
		if tag in ["img", "br"] and not oneline:
			self.handle_endtag(tag, oneline=True)


	def handle_endtag(self, tag, oneline=False):
		e = self.parsingTags[-1]
		
		[i.Check(e, endTag = True, oneline=oneline) for i in self.emmetEngine]
		self.parsingTags = self.parsingTags[:-1]

	def handle_data(self, data):
		self.parsingTags[-1].setData(data)
		self.parsingTags[0].setData(data)

	def setFilter(self, filter, ignore=[]):
		self.emmetEngine.append(Emmet(filter, ignore=ignore))
		# self.emmetEngine[-1].printTransitions()

	def getDMLS(self):
# 		for i in self.emmetEngine:
# 			print(i.dataMappingList)
		dmls = [[{z[0]:z[1] for z in dml} for dml in i.dataMappingList] for i in self.emmetEngine]
# 		print(dmls)
		return dmls

	def parse(self):
		self.feed(self.html)
