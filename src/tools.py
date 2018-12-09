"""
tools.py
written by ariyn
"""
from random import randrange
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from copy import copy
from zipfile import ZipFile
from tempfile import NamedTemporaryFile

import json
import unicodedata
import re
import multiprocessing
import os
import time
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler


GetHost = lambda url: url.replace("http://", "").replace("https://", "").split("/")[0]
lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def __randomHeader__(host=''):
	version = (randrange(40, 55, 1), randrange(0, 60, 1), randrange(2500, 3500))
	mozilla = "Mozilla/%d.0 (Windows NT 6.1)"%(version[0]//10)
	webkit = "AppleWebKit/%d.%d (KHTML, like Gecko)"%(version[0], version[1])
	chrome = "Chrome/%d.0.%d.115"%(version[1], version[2])
	safari = "Safari/%d.%d"%(version[0], version[1])

	agent = "%s %s %s %s"%(mozilla, webkit, chrome, safari)
	return version, {
          "Accept":"text/html,application/xhtml+xml,application/xml;"+
                   "q=0.9,image/webp,image/apng,*/*;q=0.8",
          "Accept-Encoding":"gzip, deflate",
          "Accept-Language":"ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4",
          "Cache-Control":"max-age=0",
          "Connection":"keep-alive",
          "Host":host,
          "Upgrade-Insecure-Requests":"1",
          "User-Agent":agent
        }

randomHeader = lambda host='': copy(__randomHeader__(host)[1])

def multiDownload(path, referer, urls, interval=0.5, chunkSize=5):
	"""
	download several urls

	urls structure must be changed
	"""

	headers = randomHeader()
	headers["Referer"] = referer

	processList = []
	headers["Host"] = GetHost(urls[0][1])

	newUrls = []
	for i in range(0, len(urls), chunkSize):
		newUrls.append(urls[i:i+chunkSize])

	with Log() as log:
		for i,v in enumerate(newUrls):
			p = multiprocessing.Process(target=__downloadProcess__, args=(path, headers, v, interval, i, log))
			processList.append(p)
			p.start()

	for p in processList:
		p.join()

def __downloadProcess__(path, header, urls, interval, index, logger):
	for i in urls:
		try:
			req = Request(i[1], headers=header)
			res = urlopen(req)

			x = open(path+"/"+i[0], "wb")
			x.write(res.read())
			x.close()

		except HTTPError as e:
			logger.error('download error to %s', path, extra = {
				"code":str(e.code),
				"reason":e.reason,
				"url":i[1]
			})

		time.sleep(interval)

def escapeFilenames(value):
	"""
	escape file names for linux file system
	"""
	value = unicodedata.normalize('NFKD', value)#.encode('utf-8')
	value = re.sub(r'[^\w\s-]', '', value).strip().lower()
	value = re.sub(r'[-\s]+', '-', value)

	return value

def compressFile(name, target, destination, removeOriginal=False):
	"""
	compress file
	"""
	try:
		fileList = os.listdir(target)
	except NotADirectoryError:# as e:
		return 0

	fileName = "%s/%s.zip"%(destination, name)
	z = ZipFile(fileName, "w")

	for i in fileList:
		if ".zip" not in i:
			z.write(target+"/"+i, i)

	ret = z.testzip()

	if ret is not None:
		print("First bad file in %s.zip: %s" % (name, ret))
	z.close()

	if removeOriginal and ret is None:
		for i in fileList:
			os.remove(target+"/"+i)
		os.rmdir(target)

	return fileName

## cookie manager must be singleton instance
class __cookieManager__:
	keywords = ["set-cookie", "host", "date"]

	def __saveCookies__(self):
		for key in self.changedCookie:
			with open("%s/%s"%(self.userDir, key), "w") as file:
				file.write(self.__get__(key))

	def __init__(self):
		from sys import platform
		import atexit
		from pathlib import Path

		self.cookies = {}
		self.changedCookie = set()
		### is linux
		if platform == "linux" or platform == "linux2" or platform == "darwin":
			userDir = "%s/.cookies"%str(Path.home())
			if not os.path.isdir(userDir):
				os.mkdir(userDir)
		elif platform == "win32":
			userDir = "%s/Documents/cookies"%(os.environ['USERPROFILE'])
			if not os.path.isdir(userDir):
				os.mkdir(userDir)

		list = os.scandir(userDir)
		for file in list:
			if not file.name.startswith('.') and file.is_file():
				cookieStr = open(file.path, "r").read()
				cookie= __cookieManager__.parseCookie(cookieStr)
				if cookieStr == "":
					continue
				self.cookies[file.name] = {}
				self.cookies[file.name].update(cookie)
		self.userDir = userDir
# 		print(self.__saveCookies__)
		atexit.register(self.__saveCookies__)

	@staticmethod
	def parseCookie(cookie):
		pc = [i.strip().split("=") for i in cookie.split(";")]
		pc = [i if len(i) == 2 else [i[0], i[0]] for i in pc]
		return pc

	def __add__(self, domain, cookie):
		if domain not in self.cookies:
			self.cookies[domain] = {}

		cookie = __cookieManager__.parseCookie(cookie)
		# https://tools.ietf.org/html/rfc6265#section-5.2
		self.cookies[domain].update(cookie)
		self.changedCookie.add(domain)

	def __get__(self, domain):
# 		print(domain)
		if domain in self.cookies:
			return "; ".join(["%s=%s"%(k, v) for k,v in self.cookies[domain].items()])
		else:
			return ""

	def __getitem__(self, key):
		return self.__get__(key)
	def __setitem__(self, key, value):
		return self.__add__(key, value)

class Log:
	debugFile = NamedTemporaryFile(suffix=".log", prefix="crawl-", delete=False)
	path = "./log/crawl.log"
	debug = False
	format = "%(asctime)-15s %(url)s %(message)s %(code)-3s\n\t%(reason)s\n"

	def __init__(self, name="crawler", path=None, format=None, debug=False):
		debug = debug or self.debug
		if format is None:
			format = Log.format
		self.log = logging.getLogger(name)
		if not hasattr(self.log, "stdFileHandler"):
			setattr(self.log, "stdFileHandler", False)
			setattr(self.log, "stdStreamHandler", False)

		self.log.setLevel(logging.INFO if not debug else logging.DEBUG)
		self.formatter = logging.Formatter(format)

		if path is not None:
			self.path = path
# 		if debug:
# 			self.path = self.debugFile.name

		if not self.log.stdFileHandler:
			fileHandler = RotatingFileHandler(self.path, maxBytes=1024*1024)
			fileHandler.setFormatter(self.formatter)
			self.log.addHandler(fileHandler)
			self.log.stdFileHandler = True

		if debug and not self.log.stdStreamHandler:
			streamHandler = logging.StreamHandler()
			streamHandler.setFormatter(self.formatter)
			self.log.addHandler(streamHandler)
			self.log.stdStreamHandler = True

	def __enter__(self):
		self.log.__parent__ = self
		return self.log

	def __exit__(self, exc_type, exc_value, traceback):
		pass

CookieManager = __cookieManager__()
