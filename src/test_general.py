import unittest
from htmlnode import string_dict, HTMLNode, LeafNode, ParentNode
from supporting import split_nodes_delimiter, extract_markdown_images, split_nodes_image, text_to_textnodes
from textnode import TextNode, TextType


class TestStringDict(unittest.TestCase):
    def test_basic_pair(self):
        self.assertEqual(string_dict(("class", "btn")), ' class="btn"')

    def test_empty_key(self):
        # even an empty key yields a leading space
        self.assertEqual(string_dict(("", "value")), ' ="value"')

    def test_empty_value(self):
        # empty value is still wrapped in quotes
        self.assertEqual(string_dict(("data", "")), ' data=""')


class TestHTMLNodePropsToHtml(unittest.TestCase):
    def test_no_props(self):
        node = HTMLNode("p", None, None, None)
        self.assertEqual(node.props_to_html(), "")

    def test_multiple_props_order(self):
        # dict insertion order should be preserved in string
        props = {"id": "main", "class": "container"}
        node = HTMLNode("div", None, None, props)
        self.assertEqual(
            node.props_to_html(),
            ' id="main" class="container"'
        )


class TestHTMLNodeRepr(unittest.TestCase):
    def test_repr_all_fields(self):
        node = HTMLNode("span", "txt", [], {"href": "u"})
        self.assertEqual(
            repr(node),
            "HTMLNode(span, txt, children: [], {'href': 'u'})"
        )


class TestLeafNodeErrors(unittest.TestCase):
    def test_missing_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_no_tag_returns_raw(self):
        node = LeafNode(None, "just text")
        self.assertEqual(node.to_html(), "just text")


class TestParentNodeErrors(unittest.TestCase):
    def test_missing_tag_raises(self):
        node = ParentNode(None, [LeafNode("b", "x")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_missing_children_raises(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()


class TestParentNodeExtra(unittest.TestCase):
    def test_multiple_siblings(self):
        c1 = LeafNode("i", "one")
        c2 = LeafNode("u", "two")
        parent = ParentNode("p", [c1, c2])
        self.assertEqual(
            parent.to_html(),
            "<p><i>one</i><u>two</u></p>"
        )

    def test_parent_props_are_ignored(self):
        # current impl doesn’t render props on ParentNode
        children = [LeafNode("span", "hi")]
        p_with_props = ParentNode("div", children, {"data": "x"})
        p_without = ParentNode("div", children)
        self.assertEqual(p_with_props.to_html(), p_without.to_html())


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_simple_pairing(self):
        # one pair of delimiters around a word
        nodes = [TextNode("foo*bar*baz", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        # Expect: ["foo" (TEXT), "bar" (ITALIC), "baz" (TEXT)]
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], TextNode("foo", TextType.TEXT))
        self.assertEqual(result[1], TextNode("bar", TextType.ITALIC))
        self.assertEqual(result[2], TextNode("baz", TextType.TEXT))

    def test_passthrough_non_text_nodes(self):
        # nodes whose text_type != TEXT should be unmodified
        nt = TextNode("unchanged", TextType.BOLD, url="http://")
        result = split_nodes_delimiter([nt], "#", TextType.ITALIC)
        self.assertEqual(result, [nt])

    def test_mixed_node_list(self):
        # mix TEXT and LINK nodes
        t1 = TextNode("pre*in*post", TextType.TEXT)
        t2 = TextNode("link", TextType.LINK, url="u")
        combined = [t1, t2]
        result = split_nodes_delimiter(combined, "*", TextType.ITALIC)
        # first splits into 3, second stays as-is → total 4
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], TextNode("pre", TextType.TEXT))
        self.assertEqual(result[1], TextNode("in", TextType.ITALIC))
        self.assertEqual(result[2], TextNode("post", TextType.TEXT))
        self.assertEqual(result[3], t2)

    def test_empty_input_returns_empty(self):
        self.assertEqual(split_nodes_delimiter([], "@", TextType.CODE), [])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE,
                         "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        self.assertEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE,
                         "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ], new_nodes,
        )


if __name__ == "__main__":
    unittest.main()
