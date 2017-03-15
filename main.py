""" This file use for running pcrawler, see README.md for detail """
import sys
import urllib.request
from bs4 import BeautifulSoup
import json
import re
from functools import reduce

class Crawler:
    """
    This crawler will follow configuration file for fetching data on HTML document
    """

    def __init__(self, filename):
        """ load configuration """
        self.config = self._load_configuration(filename)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', self.config["user_agent"])]
        self.opener = opener
        self.result = {}
        self.results = []

    @staticmethod
    def _load_configuration(filename):
        """ load configuration to instance
        Args:
          filename: filename in current directory
        Return:
          config: dict foramt
        Raise:
          TODO: ConfigurationError if format incorrect
          FileNotFoundError if file not find
        """
        with open(filename) as json_data_file:
            data = json.load(json_data_file)
        return data

    @staticmethod
    def _extract_text_node(document, css_path, value_format, multiple=False):
        """ return value of target node """
        soup = BeautifulSoup(document, "html.parser")
        els = soup.select(css_path)
        if len(els):
            if multiple:
                return '\n'.join([x.text.strip() for x in els]).strip()
            else:
                if value_format == "number":
                    price = re.findall(r"[-+]?\d+[\.]?\d*", els[0].text.strip())
                    return float(price[0])
                return els[0].text.strip()
        else:
            raise ValueError("Cannot find node css_path:%s" % css_path)

    def _extract_link_node(self, document, css_path, nested_properties):
        """ update dict value of nested target node """
        a_links = BeautifulSoup(document, "html.parser").select(css_path)
        if len(a_links) > 0:
            url = a_links[0]["href"]
            content = self.opener.open(url).read()
            for p in nested_properties:
                self._content_router(content, p)

    def _content_router(self, document, l_property):
        """ Set the result to instance
        Args:
          document: could be part of the html, does not need to be <html>
          l_property: contain information of the lookup
        """
        if l_property["type"] == "text":
            self.result[l_property["name"]] = self._extract_text_node(
                document, l_property["css_path"], l_property["format"], l_property["multiple"])
        elif l_property["type"] == "sizeof":
            self.result[l_property["name"]] = self._extract_size_node(document)
        elif l_property["type"] == "link":
            self._extract_link_node(
                document, l_property["css_path"], l_property["nested_properties"])

    @staticmethod
    def _extract_size_node(document):
        """ return size in kb of target document
        Args:
          document: content in string
        Return:
          config: size in kb
        Raise:
          ValueError if document is None
        """
        if not document is None:
            return "%.2fkb" % (sys.getsizeof(document) * 8 / 1024)
        else:
            raise ValueError("Missing document input")

    def _output_results(self):
        """ output result to txt file """
        reducers = self.config["reducers"]
        addon = {}
        for r in reducers:
            if r["type"] == "sum":
                n = r['name']
                k = r['key']
                v = 0
                for x in self.results:
                    v += x[k]
                addon[n] = round(v, 2)

        to_dump = {
            'results': self.results,
        }
        to_dump.update(addon)

        r_json = json.dumps(to_dump)

        filename = self.config["filename"]
        with open(filename, 'w') as f:
            f.write(r_json)
        return to_dump

    def start(self):
        """ This method will crawl data accroding to configuration file,
        result will be output in directory
        TODO: show % progress in stdout
        1. crawl url -> root document,
        2. pass to countent router to decide what to do
        3. output result
        """
        url = self.config["document_url"]
        l_properties = self.config["lookup_properties"]
        content = self.opener.open(url).read()
        items = BeautifulSoup(content, "html.parser").select(
            self.config["items_css_path"])
        results = []
        for item in items:
            self.result = {}
            for p in l_properties:
                self._content_router(str(item), p)
            results.append(self.result)
        self.results = results
        return self._output_results()

if __name__ == "__main__":
    _config = sys.argv[1]
    _crawler = Crawler(_config)
    result_dict = _crawler.start()
    # result_dict for external module,
    # check sainsbury.json in directory
