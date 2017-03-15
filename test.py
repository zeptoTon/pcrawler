import unittest
from unittest.mock import patch, Mock
import subprocess
from main import Crawler
import urllib.request
import json


class TestStringMethods(unittest.TestCase):
    """
    Test Case has coverd all function, we use mock to replace url reqeust.
    """

    def setUp(self):
        with open('test/htmldoc.txt', 'r') as d:
            self.doc = d.read()
        self.crawler = Crawler("test/test_correct.config.json")
        self.result = {}

    def tearDown(self):
        pass

    def test_loading_config(self):
        self.assertRaises(FileNotFoundError, Crawler._load_configuration,
                          "test/test_wrong.config.txt")

    def test_extract_size_node(self):
        self.assertEqual("660.87kb", Crawler._extract_size_node(self.doc))

    def test_extract_text_node(self):
        self.assertEqual("Sainsbury's Apricot Ripe & Ready x5",
                         Crawler._extract_text_node(self.doc,
                                                    "#productLister > ul > li:nth-of-type(1) > div.product" +
                                                    " > div > div.productInfoWrapper > div > h3 > a",
                                                    "string"))
        self.assertEqual(1.50, Crawler._extract_text_node(self.doc,
                                                          "#addItem_572163 > div.pricing > p.pricePerUnit", "number"))

    @patch("urllib.request.OpenerDirector.open")
    def test_extract_link_node(self, mock_open):
        a = Mock()
        with open("test/example1.html") as c:
            e1 = c.read()
        with open("test/example2.html") as c:
            e2 = c.read()
        a.read.side_effect = [e1, e2]
        mock_open.return_value = a
        nested_properties = [
            {
                "type": "sizeof",
                "name": "size",
                "format": "string"
            },
            {
                "type": "text",
                "name": "description",
                "multiple": True,
                "format": "string",
                "css_path": "div.description > p"
            }
        ]
        css_path = "#productLister > ul > li:nth-of-type(3) > div.product > div > div.productInfoWrapper > div > h3 > a"

        expected_result = {
            "size": "2.05kb",
            "description": "E\nX\nA\nM\nP\nL\nE\n1",
        }
        self.crawler._extract_link_node(self.doc, css_path, nested_properties)
        for k in expected_result:
            self.assertEqual(self.crawler.result[k], expected_result[k])

    @patch("urllib.request.OpenerDirector.open")
    def test_start(self, mock_open):
        a = Mock()
        with open("test/example.html") as c:
            ex = c.read()
        with open("test/example1.html") as c:
            e1 = c.read()
        with open("test/example2.html") as c:
            e2 = c.read()
        a.read.side_effect = [ex, e1, e2]
        mock_open.return_value = a
        r = {
            "results": [
                {
                    "title":  "Example 1",
                    "size": "2.05kb",
                    "unit_price": 11.11,
                    "description": "E\nX\nA\nM\nP\nL\nE\n1"
                },
                {
                    "title":  "Example 2",
                    "size": "2.05kb",
                    "unit_price": 22.22,
                    "description": "E\nX\nA\nM\nP\nL\nE\n2"
                }
            ],
            "total": 33.33
        }
        self.assertEqual(self.crawler.start(), r)

    def test_output_results(self):
        with open('test/test_sainsbury.json') as c:
            t = json.load(c)
        with open('test/example_result.json') as c:
            r = json.load(c)
        self.assertEqual(t, r)

if __name__ == '__main__':
    unittest.main()
