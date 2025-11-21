import os


def fix_imports_in_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    if "from src" in content:
        print(f"Fixing imports in {file_path}")
        content = content.replace("from src", "from code.src")
        with open(file_path, "w") as f:
            f.write(content)


def fix_imports_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                fix_imports_in_file(os.path.join(root, file))


if __name__ == "__main__":
    fix_imports_in_directory("code/src")
