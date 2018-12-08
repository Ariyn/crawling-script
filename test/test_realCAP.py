import unittest

import os
import logging

from src.decorators import crawl
import src.EmmetNode as nsp
from src.Emmet import Emmet
from src.HTML import Element, MyHTMLParser
from src.tools import Log

@crawl
def crawler(html):
	return html

class Tester(unittest.TestCase):
	scripts = [
		"article.Story--large.Story--stagger.p-2.Story>a>div>img.d-block{image:=src}",
		"form>(dl>dt>label{text:=body})+(dl>dt>label{text2:=body})+(dl>dt>label{text3:=body})",
		"h1{title:=body}"
	]

	@staticmethod
	def setUpClass():
# 		format = "%(asctime)-15s %(message)s %(datas)s"
# 		Log.format = format
		Log.debug = True
		Tester.logger = Log()
		Tester.log = Tester.logger.log

		with open("sample/github.utf8.html","rb") as f:
			Tester.htmlString = f.read().decode("utf-8")
		with open("sample/example.utf8.html","rb") as f:
			Tester.htmlExampleString = f.read().decode("utf-8")

	def setUp(self):
		pass
	@unittest.skip("")
	def test_real_github_html_sample(self):
		html = MyHTMLParser()
		html.setFilter(self.scripts[0])
		html.parse(self.htmlString)
		print(html.getDMLS())

	@unittest.skip("")
	def test_real_github_html_sample2(self):
		html = MyHTMLParser()
		html.setFilter(self.scripts[1])
		html.parse(self.htmlString)
		print(html.getDMLS())

	@unittest.skip("")
	def test_real_cloudflare_protection_sample(self):
		res = crawler("https://manaaspace.net/p/OvRo41J9NljMgbJ24ZbE3d7L06ZAmYzx")
		print(res.isCfChallenge())
		print(res.code, res.headers.get("Server", "").startswith("cloudflare"), "jschl_vc" in res.html, "jschl_answer" in res.html)

	def test_real_example_html_sample(self):
		html = MyHTMLParser()
		html.setFilter(self.scripts[2])
		html.parse(self.htmlExampleString)
		print(html.getDMLS())