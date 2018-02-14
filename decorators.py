from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from gzip import decompress
from random import randrange

from .HTML import MyHTMLParser
from .tools import GetHost, randomHeader

headers = randomHeader()
def crawl(f):
	import inspect

	spec = inspect.signature(f)
	args = spec.parameters.items()
# 	args = [(i, False if v.default == inspect.Parameter.empty else True, None if v.default == inspect.Parameter.empty else v.default) for i, v in spec.parameters.items()]

	def _(url, *args, **kwargs):
		quotes = quote
		save = False
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

		if "quote" in kwargs:
			if not kwargs["quote"]:
				quotes = lambda x:x
			del kwargs["quote"]

		if "save" in kwargs:
			save = kwargs["save"]
			del kwargs["save"]


		if "://" not in url:
			sUrl = "http://"+url
		sUrl = url.split("://")

		pUrl = sUrl[1].split("?")
		url = sUrl[0]+"://"+quotes(pUrl[0])+(("?"+"?".join(pUrl[1:])) if len(pUrl) != 1 else "")

		print(url)
		req = Request(url, headers=headers)
		try:
			res = urlopen(req)
			html = res.read()
			
			if res.getheader("Content-Encoding") == "gzip":
				html = decompress(html)
				
			html = html.decode("utf-8")
		except URLError as e:
			print(e)
			return False


		if save:
			open(save, "w").write(html)
		return f(html, *args, **kwargs)

	return _

def crawlTest(f):
	import inspect

	spec = inspect.signature(f)
	args = spec.parameters.items()

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


def parser(src):
	def _(f):
		def __(html, *args, **kwargs):
			if type(html) == str:
				d = MyHTMLParser()
				d.html = html
			elif type(html) == MyHTMLParser:
				d = html

			d.setFilter(src)
			if f.__name__ != "__":
				d.parse()
			return f(d, *args, **kwargs)

		return __

	return _
