"""
decorators
this module contains decorators such as @crawl, @parser
"""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode

from gzip import decompress
from random import randrange

from .HTML import MyHTMLParser
from .tools import GetHost, randomHeader, Log

headers = randomHeader()
def crawl(f):
	"""
	@crawl(url [, referer, host, data, quote, save])
		this function will crawl urlpage
		url : target url
		referer : referer url string
		host : host string.
			usually you don't need to use this argument
		data : data to send.
			for now, this function will only works for GET method.
		quote : True | False
			default False. if True, this function will quote url
		save : String | None
			default None. this function will save to 'path/to/' string.
	"""
	import inspect

	spec = inspect.signature(f)
# 	args = spec.parameters.items()

	def _(url, *args, **kwargs):
		quotes = quote
		save = False
		data = None

		if "referer" in kwargs:
			headers["Referer"] = kwargs["referer"]
			if "referer" not in args:
				del kwargs["referer"]
		else:
			headers["Referer"] = url

		if "host" in kwargs:
			headers["Host"] = kwargs["host"]
			if "host" not in args:
				del kwargs["host"]
		else:
			headers["Host"] = GetHost(url)

		if "data" in kwargs:
			data = urlencode(kwargs["data"]).encode("utf-8")
			del kwargs["data"]

		if "quote" in kwargs:
			if not kwargs["quote"]:
				quotes = lambda x: x
			del kwargs["quote"]

		if "save" in kwargs:
			save = kwargs["save"]
			del kwargs["save"]


		if "://" not in url:
			sUrl = "http://"+url
		sUrl = url.split("://")

		pUrl = sUrl[1].split("?")
		url = sUrl[0]+"://"+quotes(pUrl[0])+(("?"+"?".join(pUrl[1:])) if len(pUrl) != 1 else "")
		req = Request(url, headers=headers, data=data)
		with Log() as log:
			try:
				res = urlopen(req)
				html = res.read()

				if res.getheader("Content-Encoding") == "gzip":
					html = decompress(html)

				html = html.decode("utf-8")

				log.info("crawling succeed", extra={
					"url":url,
					"code":str(res.getcode()),
					"reason":""
				})
			except URLError as e:
				log.error('crawling error', extra = {
					"code":str(e.code),
					"reason":e.reason,
					"url":url
				})
				return False


		if save:
			open(save, "w").write(html)
		return f(html, *args, **kwargs)

	return _

def crawlTest(f):
	import inspect

	spec = inspect.signature(f)
# 	args = spec.parameters.items()

	def _(file, *args, **kwargs):
		if "referer" in kwargs and "referer" not in args:
			del kwargs["referer"]

		if "host" in kwargs and "host" not in args:
			del kwargs["host"]
		print(file)
		if hasattr(file, "read"):
			html = file.read()
		else:
			html = open(file, "r").read()
		return f(html, *args, **kwargs)

	return _


def parser(src, ignore=[]):
	def _(f):
		def __(html, *args, **kwargs):
			if type(html) == str:
				d = MyHTMLParser()
				d.html = html
			elif type(html) == MyHTMLParser:
				d = html

			d.setFilter(src, ignore)
			if f.__name__ != "__":
				d.parse()
			return f(d, *args, **kwargs)

		return __

	return _
