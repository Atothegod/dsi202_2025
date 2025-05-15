with open("README.md", "r", encoding="utf-8") as file:
    text = file.read()
    words = text.split()
    print(f"Total words: {len(words)}")