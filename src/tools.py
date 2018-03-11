"""
tools.py
written by ariyn
"""
from random import randrange
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from copy import copy
from zipfile import ZipFile

import json
import unicodedata
import re
import multiprocessing
import os
import time


GetHost = lambda url: url.replace("http://", "").replace("https://", "").split("/")[0]

def __randomHeader():
	version = (randrange(40, 55, 1), randrange(0, 60, 1))
	mozilla = "Mozilla/%d.0 (Windows NT 6.1)"%(version[0]//10)
	webkit = "AppleWebKit/%d.%d (KHTML, like Gecko)"%(version[0])
	chrome = "Chrome/%d.0.%d.115"%(version[1], randrange(2500, 3500))
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

randomHeader = lambda: copy(__randomHeader()[1])

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

	for i in newUrls:
		p = multiprocessing.Process(target=_downloadProcess, args=(path, headers, i, interval))
		processList.append(p)
		p.start()

	for p in processList:
		p.join()

def _downloadProcess(path, header, urls, interval):
	for i in urls:
		try:
			req = Request(i[1], headers=header)
			res = urlopen(req)
# 			open(path+"/"+i[1].split("/")[-1], "wb").write(res.read())
			open(path+"/"+i[0], "wb").write(res.read())
			print(path+"/"+i[0])
		except HTTPError as e:
			x = open("error", "a")
			x.write(
				json.dumps({
					"error":str(e),
					"path":path,
					"url":i[1]
				})
			)
			x.close()
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
