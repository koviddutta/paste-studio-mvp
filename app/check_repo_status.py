import os
import logging

REQUIRED_FILES = [
    ".env.example",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "app/database/schema.sql",
    "push_to_github.sh",
    "rules.md",
]


def check_status():
    """
    Checks for the existence of critical repository files.
    """
    print("""=== FILESYSTEM VERIFICATION ===
""")
    missing = []
    present = []
    for file_path in REQUIRED_FILES:
        exists = os.path.exists(file_path)
        status = "✅ PRESENT" if exists else "❌ MISSING"
        print(f"{status}: {file_path}")
        if exists:
            present.append(file_path)
            try:
                size = os.path.getsize(file_path)
                print(f"         Size: {size} bytes")
            except OSError as e:
                logging.exception(f"Error getting file size: {e}")
                print("         Size: Unknown")
        else:
            missing.append(file_path)
        print()
    print("=" * 50)
    print(f"Present: {len(present)}/{len(REQUIRED_FILES)}")
    print(f"Missing: {len(missing)}/{len(REQUIRED_FILES)}")
    if missing:
        print("""
⚠️  FILES STILL MISSING:""")
        for f in missing:
            print(f"   - {f}")
        print("""
👉 Run 'python -m app.restore_github_files' to restore them.""")
    else:
        print("""
✨ All critical files are verified present.""")


if __name__ == "__main__":
    check_status()