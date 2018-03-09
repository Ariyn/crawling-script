from zipfile import ZipFile
import boto3
import os

def compressFile(name, path, removeOriginal=False):
	try:
		fileList = os.listdir(path)
	except NotADirectoryError as e:
		return 0

	fileName = "files/zip/%s.zip"%(name)
	z = ZipFile(fileName, "w")

	for i in fileList:
		if ".zip" not in i:
			z.write(path+"/"+i, i)
	print("file write done")
	z.close()
	print("closed")

	if removeOriginal:
		for i in fileList:
			os.remove(i)

	return fileName

def collect():
	import re
	comics = []
	exp = re.compile(r"(.+?) ?([0-9]+(?:화|권))")

	path = "files/zip/"
	files = os.listdir(path)
	for i in files:
		try:
			matches = exp.match(i).groups()
			folder = path+matches[0]

			if matches[0] not in comics:
				comics.append(matches[0])
				os.mkdir(folder)

			os.rename(path+i, folder+"/"+i)
		except AttributeError:
			print(i)

	print(comics)
if __name__ == "__main__":
	collect()
