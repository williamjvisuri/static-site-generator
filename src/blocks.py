

from enum import Enum
import re
from htmlnode import ParentNode


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
