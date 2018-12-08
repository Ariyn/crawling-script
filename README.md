## Crawling script
<img src="https://travis-ci.org/Ariyn/crawling-script.svg?branch=master">

this project is emmet coding style crawling script. more likely to say Selector.

## usuage
```python
from decorators import crawling, parser

@crawling
@parser("div.test>img{imageUrl:=src}+h2{imageTitle:=body}")
def crawlingImage(dmls):
	dmls = dmls.getDmls()
	print(dmls["imageUrl"], dmls["imageTitle"])

crawlingImage("http://example.org")
```
