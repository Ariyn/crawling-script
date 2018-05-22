import gzip

class Response:
	successCodes = [200, 201, 202, 203, 204, 205, 206, 207, 208]

	def __init__(self, res):
		self.response = res
		self.headers = dict(res.headers) if res.headers else {}
		self.encoding = ""

		self.encoding = res.headers.get("Content-Encoding")	
		if self.encoding == "gzip":
			self.html = gzip.GzipFile(fileobj=res).read()
		else:
			self.html = res.read()

		if res.code//100 in [1, 2, 3]:
			self.success = True
		else:
			self.success = False

		self.html = self.html.decode("utf-8")
		self.cookie = res.headers.get("Set-Cookie")

		self.keys = [i for i in dir(self) if "__" not in i]

	def __getattr__(self, key):
		if key not in self.keys:
			return self.response.__getattribute__(key)