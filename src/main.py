from supporting import copy_to_docs, generate_pages_recursive
import sys


def main():
    if len(sys.argv) == 2:
        basepath = sys.argv[1]
    elif len(sys.argv) > 2:
        raise Exception("too many arguments")
    else:
        basepath = "/"
    copy_to_docs()
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
