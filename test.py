""" This file use for pcrawler unit test, see README.md for detail """
import unittest
from unittest.mock import patch, MagicMock
import json
from main import Crawler

class TestStringMethods(unittest.TestCase):
    """
    Test Case has coverd all function, we use mock to replace url reqeust.
    """

    def setUp(self):
        with open('test/htmldoc.txt', 'r') as file_content:
            self.doc = file_content.read()
        self.crawler = Crawler("test/test_correct.config.json")
        self.result = {}

    def tearDown(self):
        pass

    def test_loading_config(self):
        """ Test the protected _loading_config funtion """
        self.assertRaises(FileNotFoundError, Crawler._load_configuration,
                          "test/test_wrong.config.txt")

    def test_extract_size_node(self):
        """ Test the protected _extract_size_node funtion """
        self.assertEqual("306.13kb", Crawler._extract_size_node('39185'))

    def test_extract_text_node(self):
        """ Test the protected _extract_text_node funtion """
        self.assertEqual("Sainsbury's Apricot Ripe & Ready x5",
                         Crawler._extract_text_node(
                             self.doc,
                             "#productLister > ul > li:nth-of-type(1) > div.product" +
                             " > div > div.productInfoWrapper > div > h3 > a",
                             "string"
                         ))
        self.assertEqual(1.50,
            Crawler._extract_text_node(
                self.doc,
                "#addItem_572163 > div.pricing > p.pricePerUnit", "number"
            ))

    @patch("urllib.request.OpenerDirector.open")
    def test_extract_link_node(self, mock_open):
        """ Test the protected _extract_link_node funtion """
        content = MagicMock()
        with open("test/example1.html") as file_content:
            ex1 = file_content.read()
        with open("test/example2.html") as file_content:
            ex2 = file_content.read()
        content.read.side_effect = [ex1, ex2]
        content.__enter__.return_value = content
        mock_open.return_value = content
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
        css_path = "#productLister > ul > li:nth-of-type(3) > div.product" + \
        " > div > div.productInfoWrapper > div > h3 > a"

        expected_result = {
            "size": "0.01kb",
            "description": "E\nX\nA\nM\nP\nL\nE\n1",
        }
        self.crawler._extract_link_node(self.doc, css_path, nested_properties)
        for k in expected_result:
            self.assertEqual(self.crawler.result[k], expected_result[k])

    @patch("urllib.request.OpenerDirector.open")
    def test_start(self, mock_open):
        """ Test the start funtion """
        content = MagicMock()
        with open("test/example.html") as file_content:
            ex = file_content.read()
        with open("test/example1.html") as file_content:
            ex1 = file_content.read()
        with open("test/example2.html") as file_content:
            ex2 = file_content.read()
        content.read.side_effect = [ex, ex1, ex2]
        content.__enter__.return_value = content
        mock_open.return_value = content
        result_content = {
            "results": [
                {
                    "title":  "Example 1",
                    "size": "0.01kb",
                    "unit_price": 11.11,
                    "description": "E\nX\nA\nM\nP\nL\nE\n1"
                },
                {
                    "title":  "Example 2",
                    "size": "0.01kb",
                    "unit_price": 22.22,
                    "description": "E\nX\nA\nM\nP\nL\nE\n2"
                }
            ],
            "total": 33.33
        }
        self.assertEqual(self.crawler.start(), result_content)

    def test_output_results(self):
        """ Test comparing the result with provided example """
        with open('test/test_sainsbury.json') as file_content:
            test_content = json.load(file_content)
        with open('test/example_result.json') as file_content:
            result_content = json.load(file_content)
        self.assertEqual(test_content, result_content)

if __name__ == '__main__':
    unittest.main()
