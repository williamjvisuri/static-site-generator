import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "hello", None, {"href": "https://www.google.com"})
        props = node.props_to_html()
        real_props = " href=\"https://www.google.com\""
        self.assertEqual(props, real_props)

    def test_neq_text(self):
        node = HTMLNode("ap", "hello", None, None)
        props = node.props_to_html()
        real_props = ""
        self.assertEqual(props, real_props)

    def test_neq_url(self):
        node = HTMLNode("ap", "hello", None, {
                        "href": "https://www.google.com", "a": "link"})
        props = node.props_to_html()
        real_props = " href=\"https://www.google.com\" a=\"link\""
        self.assertEqual(props, real_props)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), "<a href=\"https://www.google.com\">Click me!</a>")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(),
                         "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )


if __name__ == "__main__":
    unittest.main()
