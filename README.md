# scrab - Fuzzy content scraper

![Python package](https://github.com/gindex/scrab/workflows/Python%20package/badge.svg?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scrab)
[![GitHub Release](https://img.shields.io/github/v/release/gindex/scrab.svg)](https://github.com/gindex/scrab/releases) 
[![GitHub Release](https://img.shields.io/pypi/v/scrab.svg)](https://pypi.org/project/scrab) 
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)


Fast and easy to use content scraper for topic-centred web pages, e.g. blog posts, news and wikis.    

The tool uses heuristics to extract main content and ignores surrounding noise. No processing rules. No XPath. No configuration.

### Installing

```shell script
pip install scrab
```

### Usage
```shell script
scrab https://blog.post
``` 

Store extracted content to a file:

```shell script
scrab https://blog.post > content.txt
``` 

### ToDo List
- [ ] Add support for lists
- [ ] Add support for scripts 
- [ ] Add support for markdown output format
- [ ] Download and save referenced images
- [ ] Extract and embed links
 
### Development
```shell script
# Lint with flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Check with mypy
mypy ./scrab
mypy ./tests

# Run tests
pytest
``` 
Publish to PyPI:
```shell script
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```
 
### License
This project is licensed under the [MIT License](README.md).

