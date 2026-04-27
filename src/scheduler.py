"""
Daily bedtime story scheduler.

Run once and leave it running — it generates a new story every day at the
time set in config/config.yaml (default 20:00).

    python src/scheduler.py

To also generate a story immediately on startup, set run_on_start: true in
config/config.yaml, or pass --now on the command line.
"""

import sys
import time
from pathlib import Path

import schedule
import yaml

from generate_story import run

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()
    story_time = config["scheduler"]["time"]
    run_on_start = config["scheduler"].get("run_on_start", False) or "--now" in sys.argv

    print(f"Bedtime story scheduler started.")
    print(f"A new story will be generated every day at {story_time}.")
    print("Press Ctrl+C to stop.\n")

    if run_on_start:
        print("Generating story now (run_on_start is enabled)…")
        run()

    schedule.every().day.at(story_time).do(run)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")
