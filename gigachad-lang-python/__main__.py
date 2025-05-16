import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: gigachad <filename.gcd>")
        sys.exit(1)
    
    filename = sys.argv[1]
    with open(filename, "r", encoding="UTF-8") as file:
        code = file.read()

if __name__ == "__main__":
    main()