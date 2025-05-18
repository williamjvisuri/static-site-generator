from textnode import TextNode, TextType
import re
import os
import shutil


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


def copy_to_public(path_extension=""):
    public_path = "/home/williamjv/repo/static-site-generator/public/" + path_extension
    static_path = "/home/williamjv/repo/static-site-generator/static/" + path_extension
    if path_extension == "":
        if os.path.exists(public_path):
            shutil.rmtree(public_path)
        os.mkdir(public_path)
        if not os.path.exists(static_path):
            raise Exception(f"{static_path} does not exist")
    stuff_in_static = os.listdir(static_path)
    print(stuff_in_static)
    for entry in stuff_in_static:
        absolute_static_path = static_path + entry
        absolute_public_path = public_path + entry
        if os.path.isfile(absolute_static_path):
            shutil.copy(absolute_static_path, absolute_public_path)
            print("copied", absolute_static_path, "to", absolute_public_path)
        else:
            os.mkdir(absolute_public_path)
            print(f"created directory {absolute_public_path}")
            copy_to_public(path_extension + f"{entry}/")
