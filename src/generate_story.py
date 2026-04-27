import os
import random
import sys
from datetime import date
from pathlib import Path

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

CONFIG_PATH = ROOT / "config" / "config.yaml"
STORIES_DIR = ROOT / "stories"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_system_prompt(config: dict) -> str:
    all_sight_words = []
    for grade_words in config["sight_words"].values():
        all_sight_words.extend(grade_words)

    sampled_words = random.sample(all_sight_words, min(15, len(all_sight_words)))

    return (
        f"You are a warm, creative bedtime story writer for children aged {config['story']['age_range']}.\n\n"
        f"Write calm, engaging one-page bedtime stories that:\n"
        f"- Use simple vocabulary appropriate for {config['story']['age_range']} year olds\n"
        f"- Are approximately {config['story']['max_words']} words — short enough to read aloud at bedtime\n"
        f"- Naturally weave in as many sight words from the list below as fit naturally\n"
        f"- Teach the given theme or lesson gently through the story, never preachy\n"
        f"- Have a peaceful, satisfying ending that helps children drift to sleep\n\n"
        f"Sight word bank — include naturally throughout the story:\n"
        f"{', '.join(sampled_words)}\n\n"
        f"Format your response exactly like this:\n"
        f"TITLE: [Story Title Here]\n\n"
        f"[Story content here, written in paragraphs]"
    )


def generate_story(config: dict) -> tuple[str, str, str]:
    """Call Gemini and return (title, story_body, theme)."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Copy config/.env.example to .env and add your key.")

    client = genai.Client(api_key=api_key)
    theme = random.choice(config["themes"])
    today = date.today().strftime("%B %d, %Y")

    try:
        response = client.models.generate_content(
            model=config["model"]["id"],
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(config),
            ),
            contents=(
                f"Write a bedtime story for {today}.\n"
                f"Theme: {theme}\n"
                f"Age group: {config['story']['age_range']} year olds"
            ),
        )
    except Exception as e:
        print(f"Error generating story from Gemini API: {e}")
        raise

    raw = response.text.strip()

    title = "A Bedtime Story"
    story_body = raw
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("TITLE:"):
            title = stripped[6:].strip()
            story_body = "\n".join(lines[i + 1:]).strip()
            break

    return title, story_body, theme


def save_story(title: str, story_body: str, theme: str) -> Path:
    STORIES_DIR.mkdir(exist_ok=True)
    config = load_config()
    today = date.today()
    filepath = STORIES_DIR / f"{today.isoformat()}.md"

    content = (
        f"# {title}\n\n"
        f"**Date:** {today.strftime('%B %d, %Y')}  \n"
        f"**Theme:** {theme}  \n"
        f"**Ages:** {config['story']['age_range']}\n\n"
        f"---\n\n"
        f"{story_body}\n"
    )

    filepath.write_text(content, encoding="utf-8")
    return filepath


def run(force: bool = False) -> None:
    """Generate and save today's story. Skips if already exists unless force=True."""
    config = load_config()

    today_file = STORIES_DIR / f"{date.today().isoformat()}.md"
    if today_file.exists() and not force:
        print(f"[SKIP] Story already exists for today: {today_file}")
        print("[SKIP] Gemini API not called. Use --force to regenerate.")
        return

    print("Generating today's bedtime story…")
    title, story_body, theme = generate_story(config)
    filepath = save_story(title, story_body, theme)

    print(f"Saved  : {filepath}")
    print(f"Title  : {title}")
    print(f"Theme  : {theme}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    run(force=force)
