import unittest
from typing import List

from scrab.parser import parse, NodeSequence, Node


def remove_trailing_whitespaces(seq: List[NodeSequence]):
    for node_seq in seq:
        for node in node_seq.nodes:
            node.text = node.text.strip()
            node.tail = node.tail.strip()


class TestParser(unittest.TestCase):

    def test_single_p(self):
        html = """
            <body>
                <h1>Page title</h1>
                <div>
                    <p>This is first sentence.</p>
                </div>
            </body>
        """

        expected = [NodeSequence([
            Node("This is first sentence.", "", 3, "p"),
        ])]

        content = parse(html)
        remove_trailing_whitespaces(content)

        self.assertEqual(content, expected)

    def test_two_consecutive_p(self):
        html = """
            <body>
                <h1>Page title</h1>
                <div>
                    <p>This is first sentence.</p>
                    <p>This is second sentence.</p>
                </div>
            </body>
        """

        expected = [NodeSequence([
            Node("This is first sentence.", "", 3, "p"),
            Node("This is second sentence.", "", 4, "p")
        ])]

        content = parse(html)
        remove_trailing_whitespaces(content)

        self.assertEqual(content, expected)

    def test_two_consecutive_div(self):
        html = """
            <body>
                <h1>Page title</h1>
                <div>
                    <div>This is first sentence.</div>
                    <div>This is second sentence.</div>
                </div>
            </body>
        """

        expected = [NodeSequence([
            Node("This is first sentence.", "", 3, "div"),
            Node("This is second sentence.", "", 4, "div")
        ])]

        content = parse(html)
        remove_trailing_whitespaces(content)

        self.assertEqual(content, expected)

    def test_two_sections(self):
        html = """
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>
                <h2>First title</h2>
                <div>
                    <p>This is first sentence.</p>
                    <p>This is second sentence.</p>
                </div>
                <h2>Second title</h2>
                <div>
                    <div>
                        <p>This is fourth sentence.</p>
                        <p>This is fifth sentence.</p>
                    </div>
                </div>
            </body>
        """

        expected = [
            NodeSequence([
                Node("This is first sentence.", "", 3, "p"),
                Node("This is second sentence.", "", 4, "p")
            ]),
            NodeSequence([
                Node("This is fourth sentence.", "", 9, "p"),
                Node("This is fifth sentence.", "", 10, "p")
            ])
        ]

        content = parse(html)
        remove_trailing_whitespaces(content)

        self.assertEqual(content, expected)

    def test_links(self):
        html = """
            <body>
                <h1>Page title</h1>
                <div>
                    <p>This is first sentence.</p>
                    <p>This is second sentence. Here <a>are</a> multiple <a>links</a> to different <a>resources</a>.</p>
                </div>
            </body>
        """

        expected = [NodeSequence(nodes=[
            Node(text="This is first sentence.", tail="", visit_time=3, tag="p"),
            Node(text="This is second sentence. Here", tail="", visit_time=4, tag="p"),
            Node(text="are", tail="multiple", visit_time=5, tag="a"),
            Node(text="links", tail="to different", visit_time=6, tag="a"),
            Node(text="resources", tail=".", visit_time=7, tag="a")])
        ]

        content = parse(html)
        remove_trailing_whitespaces(content)

        self.assertEqual(content, expected)
