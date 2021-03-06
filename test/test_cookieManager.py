import unittest

from src.tools import CookieManager
import os
from pathlib import Path

class test(unittest.TestCase):
	sampleDomain = "example.org"
	# @unittest.skip("")
	def test_cookie_create_folder(self):
		print("user folder's cookie", os.listdir(CookieManager.userDir))

	def test_cookie_set(self):
		CookieManager[self.sampleDomain] = "sample=test"

		self.assertEqual("sample=test", CookieManager[self.sampleDomain])

	# @unittest.skip("")
	def test_cookie_set_more_realistic_cookie(self):
		domain = "google.com"
		realCookie = "SIDCC=AEfoLeY-JtNWizclnCHrNUDdaasdassadasxw; expires=Wed, 19-Sep-2018 09:57:49 GMT; path=/; domain=.google.com; priority=high"
		notRealCookie = "FAKE-COOKIE=jdsflkjlkdsjlfkjdsfjlk; expires=Fri, 19-Sep-2018 09:57:49 GMT; path=/; domain=.google.com; priority=high"

		CookieManager[domain] = realCookie
		CookieManager[domain] = notRealCookie

		correctCookie = set(["SIDCC=AEfoLeY-JtNWizclnCHrNUDdaasdassadasxw", "expires=Fri, 19-Sep-2018 09:57:49 GMT", "path=/", "domain=.google.com", "priority=high", "FAKE-COOKIE=jdsflkjlkdsjlfkjdsfjlk"])

		self.assertEqual(6, len(correctCookie - set(CookieManager[domain])))
