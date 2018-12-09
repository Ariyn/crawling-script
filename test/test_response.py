import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, mock_open

import urllib.request
from urllib.error import HTTPError

from tempfile import TemporaryDirectory, NamedTemporaryFile, gettempdir

import os
import logging

from src.response import Response
from src.tools import randomHeader, Log

headers = {
	"cf-ray":"41de818afe539493-NRT",
	"content-encoding":"br",
	"content-type":"text/html; charset=utf-8",
	"date":"Sun, 20 May 2018 11:36:31 GMT",
	"expect-ct":'max-age=604800, report-uri="ht….com/cdn-cgi/beacon/expect-ct',
	"server":"cloudflare",
	"set-cookie":"_ga_remote=121.64.194.131; exp…GMT; Max-Age=31536000; Path=/",
	"vary":"Cookie",
	"X-Firefox-Spdy":"h2"
}


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
		cm.headers = headers
		cm.code = 200
		cm.msg = "OK"
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
	
# 	@mock.patch("urllib.request.urlopen")
	def test_response_structure(self, mockUrlopen=None):
		rh = randomHeader("example.org")
		request = urllib.request.Request("http://example.org", headers = rh)
		try:
			response = urllib.request.urlopen(request)
			print(dir(response))
			print(response.code, response.msg)
		except HTTPError as e:
			response = e
			res = Response(response)
		
			rh["DNT"] = 1
			rh["Cookie"] = ";".join(res.cookie).replace("HttpOnly;", "")+"; cf_use_ob=443;"
			request = urllib.request.Request("http://example.org", headers = rh)

			try:
				response = urllib.request.urlopen(request)
			except HTTPError as e:
				response = e
		
		print(type(response))
		res = Response(response)
		print(res.msg, res.code)
		print(res.getcode())
