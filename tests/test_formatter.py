import unittest

from scrab.formatter import to_text
from scrab.parser import Node, NodeSequence


class TestFormatter(unittest.TestCase):

    def test_empty(self):
        nodes = []
        content = to_text(nodes)

        self.assertEqual(content, "")

    def test_one_node(self):
        nodes = [NodeSequence([
            Node("This is beginning ", "and end of sentence.", 1, "p"),
        ])]

        expected = "\nThis is beginning and end of sentence."

        content = to_text(nodes)

        self.assertEqual(content, expected)

    def test_multiple_nodes(self):
        nodes = [NodeSequence([
            Node("This is beginning ", "and end of sentence. ", 1, "p"),
            Node("Second ", "sentence.", 1, "div"),
            Node("", "Third.", 1, "p"),
        ])]

        expected = "\nThis is beginning and end of sentence. Second sentence.\nThird."

        content = to_text(nodes)

        self.assertEqual(content, expected)
