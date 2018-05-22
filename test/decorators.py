import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import urllib.request
from urllib.error import HTTPError

# from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir

import os
from io import BytesIO
import logging

import src.decorators as decorator
from src.tools import randomHeader, Log

@decorator.crawl
def crawlGoogle(response):
	return response

class Tester(unittest.TestCase):
	returnValue = b'<html>contents</html>'
	
	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(code)-3s %(url)s %(message)s\n\t%(reason)s\n\t%(headers)s"
		Tester.formatter = logging.Formatter(format)
		Tester.log = logging.getLogger("test.decorators")
		Log.format = format
		
		Log.debug = True
	
	def setUp(self):
		cm = MagicMock()
		cm.getcode.return_value = 200
		cm.headers.return_value = {}
		cm.read.return_value = Tester.returnValue
		cm.__enter__.return_value = cm
		self.cm = cm

	@staticmethod
	def genException(number):
		msg = {
			404: "404 Page Not Found",
			503: "503 Service Unavailable"
		}
		return lambda x: Tester.raiseException(
			HTTPError(x.full_url, number, msg[number], {}, BytesIO(Tester.returnValue))
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
		self.assertEqual(html.html, Tester.returnValue.decode())

	@mock.patch('src.decorators.urlopen')
	def test_crawl_exception_404(self, mockUrlopen):
		decorator.urlopen.side_effect = Tester.genException(404)

		crawl_func = decorator.crawl(lambda x: x)
		html = crawl_func("http://example.org/")
		self.assertEqual(html.code, 404)
		self.assertEqual(html.success, False)
		
	@mock.patch('src.decorators.urlopen')
	def test_crawl_exception_503(self, mockUrlopen):
		decorator.urlopen.side_effect = Tester.genException(503)

		crawl_func = decorator.crawl(lambda x: x)
		html = crawl_func("http://example.org/")
		self.assertEqual(html.code, 503)
		self.assertEqual(html.success, False)
		
	@mock.patch('src.decorators.urlopen')
	def test_parser(self, mockUrlopen):
		parser_func = decorator.parser("div.test{text:=body}")
		data_func = parser_func(lambda x:x)
		data = data_func("<body><div class='test'>test</div><div class='test2'>test2</div></body>")
		dmls = data.getDMLS()
		self.assertEqual(dmls, [[{'text':'test'}]])
		
	def test_crawl_real_google(self):
		response = crawlGoogle("https://google.com")

# 		print(response.headers)
		self.assertEqual(response.code, 200)
		self.assertEqual(response.success, True)
# 	def test_crawl_test(self):
# 		crawl_func = decorator.crawlTest(lambda x: x)
# 		html = crawl_func("http://example.org")
# 		print(html)