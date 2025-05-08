from textnode import TextNode, TextType

def main():
    textnode = TextNode("hello", TextType.BOLD, "https://www.google.com")
    print(textnode)

if __name__ == "__main__":
    main()
