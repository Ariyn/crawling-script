import gzip

class Response:
	successCodes = [200, 201, 202, 203, 204, 205, 206, 207, 208]

	def __init__(self, res):
		self.response = res
		self.headers = {}
		if res.headers:
			for key, value in res.headers.items():
				if key in self.headers:
					if type(self.headers[key]) != list:
						self.headers[key] = [self.headers[key]]
					if type(self.headers[key]) == list:
						self.headers[key].append(value)
				else:
					self.headers[key] = value
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
		self.cookie = self.headers.get("Set-Cookie")

		self.keys = [i for i in dir(self) if "__" not in i]

	def __getattr__(self, key):
		if key not in self.keys:
			return self.response.__getattribute__(key)
	
	def isCfChallenge(self):
		return (
			self.code == 503
			and self.headers.get("Server", "").startswith("cloudflare")
			and "jschl_vc" in self.html
			and "jschl_answer" in self.html
		)

	@staticmethod
	def unzip(file, encoding="utf-8"):
		return gzip.GzipFile(fileobj=file).read().decode(encoding)
