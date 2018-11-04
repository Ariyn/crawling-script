import unittest

import apex.functions.cap.main as main
import src.decorators as decorators

@decorators.crawl
@decorators.parser("h1{title:=body}")
def testCrawl(response):
	return response.getDMLS()

class test_apex_lambda(unittest.TestCase):
	parseCase = [
		{"url":"https://example.org", "parse":["div>h1{title:=body}"]}
	]
	def test_setup(self):
		result = main.lambda_handler(self.parseCase[0], None)
		print(result)
		
		x = testCrawl("https://example.org")
		print(x)