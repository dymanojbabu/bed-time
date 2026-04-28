import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config" / "config.yaml"
STORIES_DIR = ROOT / "stories"

load_dotenv(ROOT / ".env")


def _load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_github_pr(title: str, theme: str, filepath: Path) -> None:
    """Create a GitHub PR for the newly generated story."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[PR] GITHUB_TOKEN not set in .env — skipping PR creation.")
        return

    config = _load_config()
    repo = config.get("github", {}).get("repo", "")
    if not repo:
        print("[PR] github.repo not set in config.yaml — skipping PR creation.")
        return

    today = date.today().isoformat()
    date_str = date.today().strftime("%B %d, %Y")
    branch = f"story/{today}"

    try:
        subprocess.run(["git", "checkout", "-B", branch], check=True, capture_output=True)
        subprocess.run(["git", "add", str(filepath)], check=True, capture_output=True)

        # Only commit if there is something staged
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if staged.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"story: {title} — {date_str}"],
                check=True, capture_output=True,
            )
        else:
            print("[PR] Nothing new to commit — file already committed, continuing to push.")

        subprocess.run(["git", "push", "origin", branch, "--force"], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode().strip() if e.stderr else ""
        stdout = e.stdout.decode().strip() if e.stdout else ""
        print(f"[PR] Git error: {stderr or stdout or str(e)}")
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        return

    response = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        json={
            "title": f"Bedtime Story — {date_str}",
            "body": (
                f"**Theme:** {theme}  \n"
                f"**File:** `{filepath.name}`  \n\n"
                f"New bedtime story generated automatically."
            ),
            "head": branch,
            "base": "main",
        },
    )

    if response.status_code == 201:
        print(f"[PR] Created: {response.json()['html_url']}")
    elif response.status_code == 422:
        print(f"[PR] PR already exists for branch '{branch}'.")
    else:
        print(f"[PR] Failed ({response.status_code}): {response.json().get('message', '')}")

    subprocess.run(["git", "checkout", "main"], capture_output=True)


if __name__ == "__main__":
    today_file = STORIES_DIR / f"{date.today().isoformat()}.md"

    if not today_file.exists():
        print(f"No story found for today: {today_file}")
        print("Run `python src\\generate_story.py` first to generate one.")
        sys.exit(1)

    lines = today_file.read_text(encoding="utf-8").splitlines()
    title = next((l.lstrip("# ") for l in lines if l.startswith("# ")), "A Bedtime Story")
    theme = next((l.replace("**Theme:**", "").strip().rstrip("  ") for l in lines if "**Theme:**" in l), "unknown")

    print(f"Creating PR for: {today_file.name}")
    print(f"Title : {title}")
    print(f"Theme : {theme}")
    create_github_pr(title, theme, today_file)
