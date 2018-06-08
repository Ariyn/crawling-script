import unittest

import os
import logging

import src.EmmetNode as nsp
from src.Emmet import Emmet
from src.HTML import Element, MyHTMLParser
from src.tools import Log

class Tester(unittest.TestCase):
	scripts = [
		"article.Story--large.Story--stagger.p-2.Story>a>div>img.d-block{image:=src}",
		"form>(dl>dt>label{text:=body})+(dl>dt>label{text2:=body})+(dl>dt>label{text3:=body})"
	]

	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(message)s %(datas)s"
		Log.format = format
		Log.debug = Tester.debug
		Tester.logger = Log()
		Tester.log = Tester.logger.log

		with open("sample/github.utf8.html","rb") as f:
			Tester.htmlString = f.read().decode("utf-8")

	def setUp(self):
		pass

	# @unittest.skip("")
	def test_real_github_html_sample(self):
		html = MyHTMLParser()
		html.setFilter(self.scripts[0])
		html.parse(self.htmlString)
		print(html.getDMLS())

	def test_real_github_html_sample2(self):
		html = MyHTMLParser()
		# ee = Emmet(self.scripts[1])
		# print(ee.nodes)
		# print(ee.nodes[4], ee.nodes[6], ee.nodes[8])
		html.setFilter(self.scripts[1])
		html.parse(self.htmlString)
		print(html.getDMLS())
