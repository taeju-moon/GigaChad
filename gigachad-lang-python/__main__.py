import sys
from .runtime import GigaChad


def main():
    if len(sys.argv) != 2:
        print("Usage: gigachad <filename.chad>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r", encoding="UTF-8") as file:
        code = file.read()
        compiler = GigaChad()
        compiler.compile(code)


if __name__ == "__main__":
    main()
