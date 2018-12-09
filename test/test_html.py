import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import os
import logging

from src.HTML import Element, MyHTMLParser
from src.response import Response
from src.tools import Log

class Tester(unittest.TestCase):
	capScript = [
		"div#SIvCob{title:=body}>a{language:=body}",
		"h1{title:=body}"
	]
	def test_html_parse(self):
		p = MyHTMLParser()

		with open("sample/example.html","r") as file:
			html = file.read()
			# html = Response.unzip(file)
# 			open("sample/github.utf8.html", "w").write(html)
			p.html = html
		p.setFilter(self.capScript[1])
		e = p.emmetEngine[0]
		p.parse()
		dmls = p.getDMLS()
		print(e, e.currentCapture)
		print(dmls)
