import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import urllib.request
from urllib.error import HTTPError

# from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir

import os
import logging
import re
from datetime import datetime

import src.tools as tools
from src.sample import rm

class Tester(unittest.TestCase):
	returnValue = b'<html>contents</html>'
	
	@staticmethod
	def setUpClass():
		format = "%(asctime)-15s %(code)-3s %(url)s %(message)s\n\t%(reason)s"
		Tester.formatter = logging.Formatter(format)
		Tester.log = logging.getLogger("milti-download")
		
		tools.Log.debug = True
		
	def setUp(self):
		cm = MagicMock()
		cm.getcode.return_value = 200
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
			HTTPError(x.full_url, number, msg[number], None, None)
		)
	
	@staticmethod
	def raiseException(exception):
		raise exception
	
	def test_random_header_create(self):
		version, header = tools.__randomHeader__()

#https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
	@mock.patch('src.tools.urlopen')
	def test_download_process(self, mockUrlopen):
		path, header, interval = "./test/files", tools.randomHeader(), 0
		urls = [
			("fileName1", "http://example.org/fileName1"),
			("fileName2", "http://example.org/fileName2")
		]
		
		tools.urlopen.return_value = self.cm
		with tools.Log() as log:
			tools.__downloadProcess__(path, header, urls, interval, 0, log)
			
	@mock.patch('src.tools.urlopen')
	def test_multidownload(self, mockUrlopen):
		path, header, interval = "./test/files", tools.randomHeader(), 0
		urls = [
			("fileName1", "http://example.org/fileName1"),
			("fileName2", "http://example.org/fileName2")
		]
		
		tools.urlopen.return_value = self.cm
# 			multiDownload(path, referer, urls, interval=0.5, chunkSize=5)
		tools.multiDownload(path, 'http://example.org', urls)

#	 @mock.patch('src.tools.Request')
	@mock.patch('src.tools.urlopen')
	def test_download_process_404_error(self, mockUrlopen):
		tools.urlopen.side_effect = Tester.genException(404)
		
		path, header, interval = "./test/files", tools.randomHeader(), 0
		urls = [
			("file404Name1", "http://example.org/fileName1"),
			("file404Name2", "http://example.org/fileName2")
		]
		with tools.Log() as log:
			now = datetime.now()
			strNow = now.strftime("%Y-%m-%d")

			tools.__downloadProcess__(path, header, urls, interval, 0, log)
			files = [i.baseFilename for i in log.handlers if "baseFilename" in dir(i)]
			for file in files:
				with open(file, "r") as f:
					logs = f.read().strip().split("\n\n")[-2:]
				logInfos = [re.match(r"%s .+? (.+?) download error to (.+?) (\d+)"%(strNow), logLine) for logLine in logs]

				for i, logInfo in enumerate(logInfos):
					self.assertNotEqual(logInfo, None)
					logInfo = logInfo.groups()

					self.assertEqual(logInfo[0],urls[i][1])
					self.assertEqual(logInfo[1],os.path.join(path, urls[i][0]).replace("\\","/"))
					self.assertEqual(logInfo[2], "404")

	@mock.patch('src.sample.os')
	def test_rm(self, my_mock):
		rm("sample.txt")
		
		my_mock.remove.assert_called_with("sample.txt")

	def test_logger(self):
		x = tools.Log()
		self.assertEqual(type(x), tools.Log)
		
		with tools.Log() as log:
			self.assertEqual(type(log), logging.Logger)

	def test_logger_with(self):
		format = "%(asctime)-15s %(message)s"
		with tools.Log(format=format) as log:
			pass
# 			log.info("test")

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
