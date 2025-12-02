import os
import base64
import logging
import stat
from github import Github, Auth

logging.basicConfig(level=logging.INFO, format="%(message)s")
FILES_TO_RESTORE = [
    ".env.example",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "app/database/schema.sql",
    "push_to_github.sh",
    "rules.md",
]


def restore_missing_files():
    """
    Fetches and restores missing files from the GitHub repository.
    Uses the GITHUB_TOKEN environment variable for authentication.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error("❌ GITHUB_TOKEN not found in environment variables.")
        logging.error("   Please set GITHUB_TOKEN to access the repository.")
        return
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo_name = "koviddutta/paste-studio-mvp"
        logging.info(f"🔄 Connecting to GitHub repository: {repo_name}...")
        repo = g.get_repo(repo_name)
        logging.info(f"📦 Starting restoration of {len(FILES_TO_RESTORE)} files...")
        logging.info("=" * 60)
        success_count = 0
        for file_path in FILES_TO_RESTORE:
            try:
                logging.info(f"📥 Fetching {file_path}...")
                content_file = repo.get_contents(file_path)
                if content_file.encoding == "base64":
                    content = base64.b64decode(content_file.content).decode("utf-8")
                else:
                    content = content_file.decoded_content.decode("utf-8")
                directory = os.path.dirname(file_path)
                if directory:
                    os.makedirs(directory, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                if file_path.endswith(".sh"):
                    st = os.stat(file_path)
                    os.chmod(file_path, st.st_mode | stat.S_IEXEC)
                    logging.info(f"   ⚙️  Made {file_path} executable")
                logging.info(f"   ✅ Restored ({len(content)} bytes)")
                success_count += 1
            except Exception as e:
                logging.exception(f"❌ Error restoring {file_path}: {e}")
        logging.info("=" * 60)
        if success_count == len(FILES_TO_RESTORE):
            logging.info("✨ COMPLETE: All files successfully restored!")
        else:
            logging.warning(
                f"⚠️  PARTIAL: Restored {success_count}/{len(FILES_TO_RESTORE)} files."
            )
    except Exception as e:
        logging.exception(f"❌ Critical error during restoration: {e}")


if __name__ == "__main__":
    restore_missing_files()