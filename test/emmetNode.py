import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import os
import logging

import src.EmmetNode as nsp
from src.Emmet import Emmet
from src.HTML import Element, MyHTMLParser
from src.tools import Log

class Tester(unittest.TestCase):
	scripts = [
		"tag1>  tag2",
		"[ abc := def , ghi := jkl  ]",
		"{ abc := def , ghi := jkl  }",
		"tag1>ul>(li>span[nth-sibling:=2]{title:= body})+(li>span[nth-sibling:=2]{author:=body})",
		"div>ul>(li[test:=1]>span)+(li[test:=2]>span)>sdf",
		"div#test.test1.test2{map:=data-map, list:=data-list}",
		"div#test>span{title:=body}"
	]
	html = [
		"<div id='test'>"
	]
	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(message)s %(datas)s"
		Log.format = format
		Log.debug = True
		Tester.logger = Log()
		Tester.log = Tester.logger.log
	
	def setUp(self):
		pass
	
	@unittest.skip("for test")
	def test_condition_expression(self):
		s = nsp.conditionExp.search(Tester.scripts[1])
		if s:
			s = [nsp.allocationExp.search(i.strip()) for i in s.group(1).split(",")]
			s = [i.groups() if i else i for i in s]
		Tester.log.info(msg="condition parse done", extra={"datas":str(s)})
	
	@unittest.skip("for test")
	def test_capture_expression(self):
		s = nsp.captureExp.search(Tester.scripts[2])
		if s:
			s = [nsp.allocationExp.search(i.strip()) for i in s.group(1).split(",")]
			s = [i.groups() if i else i for i in s]
		Tester.log.info(msg="capture parse done", extra={"datas":str(s)})
	
	@unittest.skip("for test")
	def test_split_token(self):
		nsp.splitToken(self.scripts[0])
	
	@unittest.skip("for test")
	def test_complex_script_split_token(self):
		nsp.splitToken(self.scripts[3])
	
	@unittest.skip("for test")
	def test_complex_script_parse(self):
		tokens = nsp.splitToken(self.scripts[3])
		root = nsp.parse(tokens)
	
	@unittest.skip("for test")
	def test_complex_script_plus_order(self):
		tokens = nsp.splitToken(self.scripts[4])
		root = nsp.parse(tokens)
		div = root.children[0]
		print(div, div.condition, div.capture, div.raw)
		root.travel()
	
	@unittest.skip("for test")
	def test_emmet_node_match(self):
		tokens = nsp.splitToken(self.scripts[5])
		root = nsp.parse(tokens)
		tag = root.travel()
	
	@unittest.skip("for test")
	def test_check_emmet(self):
		tokens = nsp.splitToken(self.scripts[5])
		root = nsp.parse(tokens).children[0]
		e = Element("div", [
			("id","test"),
			("class", "test1 test2"),
			("data-map","NY"),
			("data-list","p1,p2,p3")
		])
		self.assertTrue(root.match(e))
		
		e2 = Element("div", [
			("id","test2"),
			("class", "test1 test2"),
			("data-map","NY"),
			("data-list","p1,p2,p3")
		])
		self.assertFalse(root.match(e2))
		
		if root.match(e):
			x = root.capture(e)
			print(x)

	def test_newStyle_node_iteration(self):
		e = Emmet(self.scripts[3])
		back = False
		strs = []
		for i in e:
			strs.append(i.tag)
			if i.tag == "ul" and not back:
				e.index -= 1
				back = True
		self.assertEqual(" ".join(strs), "tag1 ul ul li span li span")

	def test_emmet_newStyle_check(self):
		elements = [Element("tag1"), Element("ul"), Element("li"), Element("span",[
			("body","testestset")
		]),Element("li"), Element("span",[
			("body","testestset")
		])]
		emmetEngine = Emmet(self.scripts[3])
		for ele in elements:
			x = emmetEngine.check(ele)
			self.assertTrue(x)
	
	def test_emmet_newStyle_check_right_elements(self):
		e = [Element("tag1"), Element("ul"), Element("li"), Element("span",[
			("body","testTitle")
		]),Element("li"), Element("span",[
			("body","testAuthor")
		])]
		
		operation = [
			(e[0], False),
			(e[1], False),
			(e[2], False),
			(e[3], False),
			(e[3], True),
			(e[2], True),
			(e[4], False),
			(e[5], False),
			(e[5], True),
			(e[4], True),
			(e[1], True),
			(e[0], True)
	]
		emmetEngine = Emmet(self.scripts[3])
		for i in range(2):
			for element, endTag in operation:
				x = emmetEngine.check(element, endTag=endTag)
# 				print(element, x)
		self.assertEqual({"title":"testTitle", "author":"testAuthor"}, emmetEngine.captures[0])

	def test_emmet_newStyle_check_wrong_elements(self):
		"""
		if emmetEngine failed to check completely (= match all elements until end)
			emmetEngine should not save currentCapture
			= emmetEngine should reset with succeed =False
		"""
		e = [Element("tag1"), Element("ul"), Element("li"), Element("span",[
			("body","testTitle")
		]),Element("li2"), Element("span",[
			("body","testAuthor")
		])]
		
		operation = [
			(e[0], False),
			(e[1], False),
			(e[2], False),
			(e[3], False),
			(e[3], True),
			(e[2], True),
			(e[4], False),
			(e[5], False),
			(e[5], True),
			(e[4], True),
			(e[1], True),
			(e[0], True)
	]
		emmetEngine = Emmet(self.scripts[3])
		for i in range(2):
			for element, endTag in operation:
				x = emmetEngine.check(element, endTag=endTag)
# 				print(element, x)
		self.assertEqual({}, emmetEngine.captures[0])