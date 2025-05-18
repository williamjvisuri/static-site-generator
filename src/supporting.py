from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import ParentNode
import re
import os
import shutil
from blocks import (
    BlockType,
    markdown_to_blocks,
    remove_newlines_from_block,
    remove_spaces_from_block,
    block_to_block_type,
    wrap_list_of_nodes_in_parent_tag,
)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            splitted = node.text.split(delimiter)
            if len(splitted) % 2 == 0:
                raise Exception("that's invalid Markdown syntax.")
            for i in range(len(splitted)):
                if splitted[i] != "":
                    if i % 2 == 0:
                        new_nodes.append(TextNode(splitted[i], TextType.TEXT))
                    else:
                        new_nodes.append(TextNode(splitted[i], text_type))
        else:
            new_nodes.append(node)
    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"\[(.*?)\]\((.*?)\)", text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            images = extract_markdown_images(node.text)
            if images == []:
                new_nodes.append(node)
            else:
                remaining_text = node.text
                for i in images:
                    image_alt, image_link = i
                    splitted = remaining_text.split(
                        f"![{image_alt}]({image_link})", 1)
                    if splitted[0] == '':
                        new_nodes.append(
                            TextNode(image_alt, TextType.IMAGE, image_link))
                    else:
                        new_nodes.append(TextNode(splitted[0], TextType.TEXT))
                        new_nodes.append(
                            TextNode(image_alt, TextType.IMAGE, image_link))
                    remaining_text = splitted[1]
                if remaining_text != "":
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            links = extract_markdown_links(node.text)
            if links == []:
                new_nodes.append(node)
            else:
                remaining_text = node.text
                for i in links:
                    link_alt, link = i
                    splitted = remaining_text.split(f"[{link_alt}]({link})", 1)
                    if splitted[0] == '':
                        new_nodes.append(
                            TextNode(link_alt, TextType.LINK, link))
                    else:
                        new_nodes.append(TextNode(splitted[0], TextType.TEXT))
                        new_nodes.append(
                            TextNode(link_alt, TextType.LINK, link))
                    remaining_text = splitted[1]
                if remaining_text != "":
                    new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        else:
            new_nodes.append(node)
    return new_nodes


def text_to_textnodes(text):
    text_node = TextNode(text, TextType.TEXT)
    bold_split = split_nodes_delimiter(
        [text_node], delimiter="**", text_type=TextType.BOLD)
    italic_split = split_nodes_delimiter(
        bold_split, delimiter="_", text_type=TextType.ITALIC)
    code_split = split_nodes_delimiter(
        italic_split, delimiter="`", text_type=TextType.CODE)
    image_split = split_nodes_image(code_split)
    link_split = split_nodes_link(image_split)
    return link_split


def copy_to_docs(path_extension=""):
    docs_path = "/home/williamjv/repo/static-site-generator/docs/" + path_extension
    static_path = "/home/williamjv/repo/static-site-generator/static/" + path_extension
    if path_extension == "":
        if os.path.exists(docs_path):
            shutil.rmtree(docs_path)
        os.mkdir(docs_path)
        if not os.path.exists(static_path):
            raise Exception(f"{static_path} does not exist")
    stuff_in_static = os.listdir(static_path)
    for entry in stuff_in_static:
        absolute_static_path = static_path + entry
        absolute_docs_path = docs_path + entry
        if os.path.isfile(absolute_static_path):
            shutil.copy(absolute_static_path, absolute_docs_path)
            print("copied", absolute_static_path, "to", absolute_docs_path)
        else:
            os.mkdir(absolute_docs_path)
            print(f"created directory {absolute_docs_path}")
            copy_to_docs(path_extension + f"{entry}/")


def extract_title(markdown):
    splitted = markdown.split("\n")
    for split in splitted:
        if split.startswith("# "):
            return split.lstrip("# ")
    raise Exception("no h1 header")


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
                if parent_node.children is None:
                    parent_node.children = pred
                else:
                    parent_node.children.extend(pred)
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
                if parent_node.children is None:
                    parent_node.children = []
                parent_node.children.extend(pred)
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
                if parent_node.children is None:
                    parent_node.children = []
                parent_node.children.extend(pred)
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
                if parent_node.children is None:
                    parent_node.children = []
                parent_node.children.extend(pred)
    return parent_node


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    entries = os.listdir(dir_path_content)
    for entry in entries:
        entry_path = f"{dir_path_content}/{entry}"
        if os.path.isfile(entry_path):
            file_name = f"{dest_dir_path}/{entry.replace(".md", ".html")}"
            generate_page(entry_path, template_path, file_name, basepath)
        else:
            generate_pages_recursive(entry_path, template_path, f"{
                                     dest_dir_path}/{entry}", basepath)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {
          dest_path} using {template_path}")
    with open(from_path) as f:
        from_contents = f.read()
    with open(template_path) as f:
        template_contents = f.read()
    html_node = markdown_to_html_node(from_contents)
    html_string = html_node.to_html()
    title = extract_title(from_contents)
    updated_template_contents = template_contents.replace(
        "{{ Title }}", title).replace("{{ Content }}", html_string).replace("href=\"/", f"href=\"{basepath}").replace("src=\"/", f"src=\"{basepath}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(updated_template_contents)
