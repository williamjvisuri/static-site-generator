from textnode import TextNode, TextType
from supporting import copy_to_public


def main():
    textnode = TextNode("hello", TextType.BOLD, "https://www.google.com")
    print(textnode)
    copy_to_public()


if __name__ == "__main__":
    main()
