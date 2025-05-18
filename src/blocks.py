

from enum import Enum
import re
from htmlnode import HTMLNode, ParentNode
from supporting import text_to_textnodes
from textnode import TextType, text_node_to_html_node, TextNode


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(md_block):
    splitted = md_block.split("\n")
    matches = re.findall(r"#{1,6} \w.*", splitted[0])
    if len(matches) == 1:
        return BlockType.HEADING
    if len(splitted) > 1 and md_block[:3] == "```" and md_block[-3:] == "```":
        return BlockType.CODE
    quote = True
    unordered = True
    ordered = True
    i = 1
    for line in splitted:
        if line[0] != ">":
            quote = False
        if line[:2] != "- ":
            unordered = False
        if line[:3] != f"{i}. ":
            ordered = False
        i += 1
    if quote:
        return BlockType.QUOTE
    if unordered:
        return BlockType.UNORDERED_LIST
    if ordered:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_blocks(markdown):
    splitted = markdown.split("\n\n")
    stripped = [x.strip() for x in splitted if x.strip() != ""]
    return stripped


def remove_newlines_from_block(block):
    splitted = block.split("\n")
    stripped = [x.strip() for x in splitted]
    return " ".join(stripped)


def remove_spaces_from_block(block):
    splitted = block.split("\n")
    stripped = [x.strip() for x in splitted]
    return "\n".join(stripped).lstrip("\n")


def wrap_list_of_nodes_in_parent_tag(nodes, tag):
    return [ParentNode(tag, nodes, None)]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent_node = ParentNode("div", None, None)
    for block in blocks:
        block_type = block_to_block_type(block)
        newline_stripped = remove_newlines_from_block(block)
        match block_type:
            case BlockType.PARAGRAPH:
                textnodes = text_to_textnodes(newline_stripped)
                tests = []
                for node in textnodes:
                    tests.append(text_node_to_html_node(node))
                if parent_node.children is None:
                    parent_node.children = wrap_list_of_nodes_in_parent_tag(
                        tests, "p")
                else:
                    parent_node.children.extend(
                        wrap_list_of_nodes_in_parent_tag(tests, "p"))
            case BlockType.HEADING:
                hashtags = newline_stripped.split()[0]
                number_of_hashtags = len(hashtags)
                textnodes = text_to_textnodes(newline_stripped.strip("# "))
                tests = []
                for node in textnodes:
                    tests.append(text_node_to_html_node(node))
                if parent_node.children is None:
                    parent_node.children = wrap_list_of_nodes_in_parent_tag(
                        tests, f"h{number_of_hashtags}")
                else:
                    parent_node.children.extend(
                        wrap_list_of_nodes_in_parent_tag(tests, f"h{number_of_hashtags}"))
            case BlockType.CODE:
                code_stripped = remove_spaces_from_block(block.strip("` "))
                coded = [text_node_to_html_node(
                    TextNode(text=code_stripped, text_type=TextType.CODE))]
                pred = wrap_list_of_nodes_in_parent_tag(coded, "pre")
                parent_node.children = pred
            case BlockType.QUOTE:
                newline_splitted = block.split("\n")
                newline_splitted[0] = newline_splitted[0][:1] + \
                    newline_splitted[0][2:]
                list_of_nodes = []
                for line in newline_splitted:
                    parsed_quote = line.split(">", maxsplit=1)[1]
                    textnodes = text_to_textnodes(parsed_quote)
                    for node in textnodes:
                        html_node = text_node_to_html_node(node)
                        list_of_nodes.append(html_node)
                pred = wrap_list_of_nodes_in_parent_tag(
                    list_of_nodes, "blockquote")
                parent_node.children = pred
            case BlockType.UNORDERED_LIST:
                newline_splitted = block.split("\n")
                list_of_nodes = []
                for line in newline_splitted:
                    tmp_nodes = []
                    parsed_number = line.split(maxsplit=1)[1]
                    textnodes = text_to_textnodes(parsed_number)
                    for node in textnodes:
                        html_node = text_node_to_html_node(node)
                        tmp_nodes.append(html_node)
                    list_of_nodes.extend(
                        wrap_list_of_nodes_in_parent_tag(tmp_nodes, "li"))
                pred = wrap_list_of_nodes_in_parent_tag(list_of_nodes, "ul")
                parent_node.children = pred
            case BlockType.ORDERED_LIST:
                newline_splitted = block.split("\n")
                list_of_nodes = []
                for line in newline_splitted:
                    tmp_nodes = []
                    parsed_number = line.split(maxsplit=1)[1]
                    textnodes = text_to_textnodes(parsed_number)
                    for node in textnodes:
                        html_node = text_node_to_html_node(node)
                        tmp_nodes.append(html_node)
                    list_of_nodes.extend(
                        wrap_list_of_nodes_in_parent_tag(tmp_nodes, "li"))
                pred = wrap_list_of_nodes_in_parent_tag(list_of_nodes, "ol")
                parent_node.children = pred
    return parent_node
