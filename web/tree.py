import os

IGNORE_DIRS = {"venv", "__pycache__", ".git", "lib"}

def build_tree(root_path=".", max_depth=3, current_depth=0, prefix=""):
    if current_depth > max_depth:
        return ""

    tree_str = ""

    try:
        items = sorted(os.listdir(root_path))
    except PermissionError:
        return ""

    for index, item in enumerate(items):
        path = os.path.join(root_path, item)

        # 🚫 Bỏ qua thư mục không cần
        if os.path.isdir(path) and item in IGNORE_DIRS:
            continue

        connector = "└── " if index == len(items) - 1 else "├── "
        tree_str += prefix + connector + item + "\n"

        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            tree_str += build_tree(
                path,
                max_depth,
                current_depth + 1,
                prefix + extension
            )

    return tree_str


# ===== CHẠY =====
root = "."
tree = os.path.abspath(root) + "\n"
tree += build_tree(root, max_depth=3)

with open("tree.txt", "w", encoding="utf-8") as f:
    f.write(tree)

print("✅ Đã xuất cây thư mục ra file tree.txt")
