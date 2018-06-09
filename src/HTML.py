"""
HTML.py
written by ariyn(himnowxz@gmail.com)

this script parse html and create elements for each tags.
"""
from html.parser import HTMLParser
from .Emmet import Emmet

class Element:
	"""
	class for html tag
	each tag will be Element instance
	"""
	MaxRecursive = 2
	def __init__(self, tag, attr=None):
		if not attr:
			attr = []
		attr = [(str(i[0]), str(i[1])) for i in attr]

		self.strAttr = []
		for v in attr:
			x = " = ".join(v) if isinstance(v[1], str) else " = ".join(" ".join(v[1]))
			self.strAttr.append(x)

		self.tag = tag
		self.parsedAttrs = {i[0]:i[1] for i in attr}
		self.id = self.parsedAttrs["id"] if "id" in self.parsedAttrs else None
		self.classes = self.parsedAttrs["class"].split(" ") if "class" in self.parsedAttrs else []
		self.data, self.children = "", []
		self.parent = None
		self.attrs = attr
# 		all-body
	def addChildren(self, child):
		"""
		add children to self
		this parent-children concept is same to html's parent-children concept
		"""
		self.children.append(child)
		child.parent = self

	def setData(self, data):
		"""
		set data of element
		data means text inside of container

		<e>lorem ipsum</e>       data:lorem ipsum
		<e><f>lorem</f>ipsum</e> data:ipsum
		"""
		self.data += data.strip()
		self.parsedAttrs["body"] = self.data

	def getAttr(self, key, retVal=None):
		"""
		REFACTORY!

		get attributes
		refactor this into __getattr__
		"""
		if key in self.parsedAttrs:
			retVal = self.parsedAttrs[key]
		return retVal

	def __str__(self):
		newData = self.data.replace("\n", "\\n")
		return "<%s %s>%s</%s>"%(self.tag, " ".join(self.strAttr), newData, self.tag)

	def printTree(self, depth=0):
		"""
		print tree structure with text
		"""
		newData = self.data.replace("\n", "\\n")
		print("%s<%s %s>%s"%("\t"*depth, self.tag, " ".join(self.strAttr), newData))

		for i in self.children:
			i.printTree(depth+1)

		print("%s</%s>"%("\t"*depth, self.tag))

class MyHTMLParser(HTMLParser):
	"""
	custom html parser
	"""
	onelineTags = ["img", "br", "input"]
	def __init__(self):
		super(MyHTMLParser, self).__init__()
		self.root = Element("Root")
		self.html = ""

		self.parsingTags = [self.root]
		self.tags = [self.root]

		self.emmetEngine = []
		self.parseEncounter = 0

	def __handle_starttag__(self, tag, attrs, oneline=False):
		e = Element(tag, attrs)
		for i in self.emmetEngine:
			i.Check(e)

		self.parsingTags[-1].addChildren(e)
		self.tags.append(e)
		self.parsingTags.append(e)

		if tag in self.onelineTags and not oneline:
			self.__handle_endtag__(tag, oneline=True)

	def __handle_endtag__(self, tag, oneline=False):
		e = self.parsingTags[-1]
		tag = tag

		for i in self.emmetEngine:
			i.Check(e, endTag=True, oneline=oneline)
		self.parsingTags = self.parsingTags[:-1]

	def handle_startendtag(self, tag, attrs):
		self.__handle_starttag__(tag, attrs, oneline=True)
		self.__handle_endtag__(tag, oneline=True)

	def handle_starttag(self, tag, attrs):
		self.__handle_starttag__(tag, attrs)

	def handle_endtag(self, tag):
		self.__handle_endtag__(tag)

	def handle_data(self, data):
		self.parsingTags[-1].setData(data)
		self.parsingTags[0].setData(data)

	def setFilter(self, _filter, ignore=None):
		"""
		create filter for emmet
		"""
		if not ignore:
			ignore = []
		self.emmetEngine.append(Emmet(_filter, ignore=ignore))

	def getDMLS(self):
		"""
		parser DMLs which Data Mapping Lists
		"""
		dmls = [i.captures for i in self.emmetEngine]
		return dmls

	def parse(self, html=None):
		"""
		wrapper of HTMLParser.feed
		"""
		if html:
			self.html = html
		self.feed(self.html)

	def error(self, x):
		pass
