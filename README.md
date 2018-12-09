## Crawling script
<img src="https://travis-ci.org/Ariyn/crawling-script.svg?branch=master">

this project is emmet coding style html Selector.

## usuage
to crawl these html page
```html
	<div class="test">
		<img src="example.org/example.png" />
		<h2>example!</h2>
	</div>
	<div class="test">
		<img src="example.org/example2.png" />
		<h2>example!!</h2>
	</div>
	<div class="test">
		<img src="example.org/example3.png" />
		<h2>example!!!</h2>
	</div>
```

you need to make decorator with specific selector.

```python
from decorators import crawling, parser

@crawling
@parser("div.test>img{imageUrl:=src}+h2{imageTitle:=body}")
def crawlingImage(dmls):
	dmls = dmls.getDmls()
	print(dmls[0]["imageUrl"], dmls[0]["imageTitle"])

crawlingImage("http://example.org")
```

result
```bash
> python3 crawl.py
example.org/example.png, example!
```

## script spec
```pre
  > : children
  + : sibling
  **: repeat (Not working currently.)
  (): has same ancestor
  {usingName:=targetName}: capturing variables. get target's value with targetName, put into usingName.
  [condition=1]: conditions. only seek right condition tags.
```
