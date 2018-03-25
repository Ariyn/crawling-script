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


GetHost = lambda url: url.replace("http://", "").replace("https://", "").split("/")[0]

def __randomHeader__():
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
          "Host":"",
          "Upgrade-Insecure-Requests":"1",
          "User-Agent":agent
        }

randomHeader = lambda: copy(__randomHeader__()[1])

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

	for i,v in enumerate(newUrls):
		p = multiprocessing.Process(target=__downloadProcess__, args=(path, headers, v, interval,i))
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

class Log:
	file = NamedTemporaryFile(suffix=".log", prefix="crawl-", delete=False)
	debug = False
	def __init__(self, name="crawler", path=None, format=None, debug=False):
		debug = debug or self.debug
		if format is None:
			format = "\n" if debug else ""
			format += "%(asctime)-15s %(url)s %(message)s %(code)-3s\n\t%(reason)s"
		self.log = logging.getLogger(name)
		self.log.setLevel(logging.INFO if not debug else logging.DEBUG)
		self.formatter = logging.Formatter(format)
		
		self.path = path
		if path is None:
			self.path = self.file.name
			
		fileHandler = logging.FileHandler(self.path)
		fileHandler.setFormatter(self.formatter)
		self.log.addHandler(fileHandler)

		if debug:
			streamHandler = logging.StreamHandler()
			streamHandler.setFormatter(self.formatter)
			self.log.addHandler(streamHandler)

	def __enter__(self):
		return self.log
	
	def __exit__(self, exc_type, exc_value, traceback):
		pass
	