# Objective
A configable crawler for html document.

## Prerequisite
python 3<br />
beautifulsoup4<br />
config.json (default provided)

## How to run
pip install -r requirement.txt <br />
python main.py config.json  <br />
The result will be ready as "sainsbury.json", you can control the filename in config.json

## Runnning test case
python test.py

## Caution
This mehtod does not suit on any javascript clientside rendering website

## config.json usage
- filename: control the output file name
- user_agent: the ua when requesting the site
- document_url: we are targeting sainsbury site, however it is also workable for other site.
- items_css_path: expecting a CSS selector for a list of product element
- lookup_properties: A list of things to lookup on the target site.
  - there are 3 type of properties (text, link, sizeof).
  - name: to specify the output key name in json
  - multiple: if True, we will concat the value with \n for selected elements
  - format: output format in json of this value
  - css_path: selector under the **items_css_path**, could select more than 1
  - nested_properties: only apply if type=link, if will follow the selected link href for next document
- reducers: do addition function for result set. Currently support sum, however it can be easily extend.
