from random import randrange
import json

from urllib.request import Request, urlopen
from urllib.error import HTTPError
import multiprocessing, os, time
from copy import copy
from zipfile import ZipFile


GetHost = lambda url:url.replace("http://", "").replace("https://", "").split("/")[0]

def __randomHeader():
	version = (randrange(40, 55, 1), randrange(0, 60, 1))
	return version, {
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"Accept-Encoding":"gzip, deflate",
		"Accept-Language":"ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4",
		"Cache-Control":"max-age=0",
		"Connection":"keep-alive",
		"Host":"",
		"Upgrade-Insecure-Requests":"1",
		"User-Agent":"Mozilla/%d.0 (Windows NT 6.1) AppleWebKit/%d.%d (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/%d.%d"%(version[0]//10, version[0], version[1], version[0], version[1])
	}

randomHeader = lambda :copy(__randomHeader()[1])

# path, referer, url
# path, url = str, str
# url = [("fileName", "url"), ...]
# path = "files/%s/%s"%(escapeFilenames(name),escapeFilenames(chapterName))
def multiDownload(path, referer, urls, interval=0.5, chunkSize=5):
	headers = randomHeader()
	headers["Referer"] = referer

	# print("path", path)

# 	try:
# 		os.mkdir(path)
# 	except FileNotFoundError as e:
# 		print(e)

	processList = []
	headers["Host"] = GetHost(urls[0][1])

	newUrls = []
	for i in range(0, len(urls), chunkSize):
# 		url[:chunkSize]:
		newUrls.append(urls[i:i+chunkSize])

# 	print("here", newUrls)
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
			x.write(json.dumps({
				"error":str(e),
				"path":path,
				"url":i[1]
			}))
			x.close()
		time.sleep(interval)

def escapeFilenames(value):
# 	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
# 	filename = ''.join(c for c in s if c in valid_chars)
# 	filename = filename.replace(' ','_') # I don't like spaces in filenames.
# 	return filename
# 	return value.replace("/", "\/")
	import unicodedata, re
	value = unicodedata.normalize('NFKD', value)#.encode('utf-8')
	value = re.sub('[^\w\s-]', '', value).strip().lower()
	value = re.sub('[-\s]+', '-', value)

	return value

def compressFile(name, target, destination, removeOriginal=False):
	try:
		fileList = os.listdir(target)
	except NotADirectoryError as e:
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
