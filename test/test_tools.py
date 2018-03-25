import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import urllib.request
from urllib.error import HTTPError

from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir

import os
import logging

import src.tools as tools
from src.sample import rm

class ToolTester(unittest.TestCase):
	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(code)-3s %(url)s %(message)s\n\t%(reason)s"
		ToolTester.formatter = logging.Formatter(format)
		ToolTester.log = logging.getLogger("milti-download")
	
	@staticmethod
	def setLogFile(log, formatter, filePath):
		fileHandler = logging.FileHandler(filePath)
		fileHandler.setFormatter(formatter)
		log.addHandler(fileHandler)
# 	def tearDown(self):
# 		[ToolTester.log.removeHandler(i) for i in ToolTester.log.handlers]

	@staticmethod
	def raiseError(x):
		raise HTTPError(x.full_url, 404, "404 Page Not Found", None, None)
	
	def test_random_header_create(self):
		version, header = tools.__randomHeader__()
#		 print(version)
#		 print(header)
	
#https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
	@mock.patch('src.tools.Request')
	@mock.patch('src.tools.urlopen')
	def test_download_process(self, mockRequest, mockUrlopen):
		cm = MagicMock()
		cm.getcode.return_value = 200
		cm.read.return_value = b'contents'
		cm.__enter__.return_value = cm
		tools.urlopen.return_value = cm

		path, header, interval = "./test/files", tools.randomHeader(), 0
		urls = [
			("fileName1", "http://example.org/fileName1"),
			("fileName2", "http://example.org/fileName2")
		]

		with NamedTemporaryFile(prefix="test") as file:
			ToolTester.setLogFile(self.log, self.formatter, file.name)
			tools.__downloadProcess__(path, header, urls, interval, 0, self.log)

#	 @mock.patch('src.tools.Request')
	@mock.patch('src.tools.urlopen')
	def test_download_process_404_error(self, mockUrlopen):
		tools.urlopen.side_effect = ToolTester.raiseError
		
		path, header, interval = "./test/files", tools.randomHeader(), 0
		urls = [
			("file404Name1", "http://example.org/fileName1"),
			("file404Name2", "http://example.org/fileName2")
		]

		with TemporaryDirectory() as path, NamedTemporaryFile(suffix=".log", prefix="test-") as file:
			ToolTester.setLogFile(self.log, self.formatter, file.name)
			
			tools.__downloadProcess__(path, header, urls, interval, 0, self.log)
			x = os.listdir(path)
			self.assertEqual(x, [])
	
	@mock.patch('src.sample.os')
	def test_rm(self, my_mock):
		rm("sample.txt")
		
		my_mock.remove.assert_called_with("sample.txt")

	def test_logger(self):
		x = tools.Log(format="%(asctime)-15s %(message)s")
		self.assertEqual(type(x), tools.Log)

	def test_logger_with(self):
		format = "%(asctime)-15s %(message)s"
		with NamedTemporaryFile(suffix=".log", prefix="test-") as file,\
			tools.Log(path=file.name, format=format) as log:
			log.warning("test")

#https://stackoverflow.com/questions/32043035/python-3-urlopen-context-manager-mocking
	@mock.patch('urllib.request.urlopen')
	def test_sample(self, mockUrlopen):
		cm = MagicMock()
		cm.getcode.return_value = 200
		cm.read.return_value = b'contents'
		cm.__enter__.return_value = cm
		mockUrlopen.return_value = cm

		with urllib.request.urlopen('http://foo') as response:
				self.assertEqual(response.getcode(), 200)
				self.assertEqual(response.read(), b'contents')