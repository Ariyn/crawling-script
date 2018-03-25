import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import urllib.request
from urllib.error import HTTPError

from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir

import os
import logging

import src.decorators as decorator
from src.tools import randomHeader, Log

class Tester(unittest.TestCase):
	returnValue = b'<html>contents</html>'
	
	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(code)-3s %(url)s %(message)s\n\t%(reason)s"
		Tester.formatter = logging.Formatter(format)
		Tester.log = logging.getLogger("milti-download")
		
		Log.debug = True
	
	def setUp(self):
		cm = MagicMock()
		cm.getcode.return_value = 200
		cm.read.return_value = Tester.returnValue
		cm.__enter__.return_value = cm
		self.cm = cm

	@staticmethod
	def setLogFile(log, formatter, filePath):
		fileHandler = logging.FileHandler(filePath)
		fileHandler.setFormatter(formatter)
		log.addHandler(fileHandler)

	@staticmethod
	def genException(number):
		msg = {
			404: "404 Page Not Found",
			503: "503 Service Unavailable"
		}
		return lambda x: Tester.raiseException(
			HTTPError(x.full_url, number, msg[number], None, None)
		)
	
	@staticmethod
	def raiseException(exception):
		raise exception
	
	@mock.patch('src.decorators.urlopen')
	def test_crawl(self, mockUrlopen):
		decorator.urlopen.return_value = self.cm
		decorator.urlopen.side_effect = None

		crawl_func = decorator.crawl(lambda x: x)
		html = crawl_func("http://example.org/")
		self.assertEqual(html, Tester.returnValue.decode())

	@mock.patch('src.decorators.urlopen')
	def test_crawl_exception_404(self, mockUrlopen):
		decorator.urlopen.side_effect = Tester.genException(404)

		crawl_func = decorator.crawl(lambda x: x)
		html = crawl_func("http://example.org/")
		self.assertEqual(html, False)
		
	@mock.patch('src.decorators.urlopen')
	def test_crawl_exception_503(self, mockUrlopen):
		decorator.urlopen.side_effect = Tester.genException(503)

		crawl_func = decorator.crawl(lambda x: x)
		html = crawl_func("http://example.org/")
		self.assertEqual(html, False)
		
	@mock.patch('src.decorators.urlopen')
	def test_parser(self, mockUrlopen):
		parser_func = decorator.parser("div.test{text:=body}")
		data_func = parser_func(lambda x:x)
		data = data_func("<body><div class='test'>test</div><div class='test2'>test2</div></body>")
		dmls = data.getDMLS()
		self.assertEqual(dmls, [[{'text':'test'}]])