# Bedtime Story Generator

A free, automated daily bedtime story generator for children aged 6–7.
Every evening at 8 PM, it uses Google Gemini to write a calming one-page
story that weaves in sight words and teaches a gentle life lesson.

Stories are saved as Markdown files in the `stories/` folder.

---

## Features

- **Free** — Google Gemini free tier via `google-genai` SDK
- **Daily automation** — Windows Task Scheduler fires at 8 PM, no process to babysit
- **Sight word practice** — Grade 1 & 2 Dolch sight words woven naturally into every story
- **20 rotating themes** — saving money, honesty, sharing, helping at home, and more
- **Skip-if-exists** — safe to re-run; won't overwrite today's story unless you pass `--force`

---

## Quick-Start (5 steps)

### 1. Get a free Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) signed in with a **personal Gmail** (`@gmail.com`)
2. Click **Create API key → Create API key in new project**
3. Copy the key

> Note: Work or school Google accounts may have the free tier blocked. Use a personal Gmail to avoid quota errors.

### 2. Add your API key

Copy the template to create your `.env` file:

```
cd C:\Code\bed-time
copy config\.env.example .env
```

Open `.env` and replace `your_api_key_here` with your real key:

```
GEMINI_API_KEY=AIza...your_key_here...
```

**Important `.env` notes:**
- `.env` must be placed at the **project root** (`C:\Code\bed-time\.env`), not inside `config/`
- `.env` is listed in `.gitignore` — it will **never be committed to GitHub**, keeping your API key safe
- `config/.env.example` is a safe template with no real key — it is committed to GitHub so others know what to set up
- Never paste your real API key into `config/.env.example` or `README.md`

### 3. Install Python dependencies

```
pip install -r requirements.txt
```

### 4. Test it manually

```
python src\generate_story.py
```

A story for today is saved in `stories/YYYY-MM-DD.md`. Run with `--force` to regenerate.

### 5. Schedule it (runs every day at 8 PM automatically)

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
C:\Code\bed-time\scripts\setup_task.ps1
```

That's it. The story generates automatically every evening.

---

## File Structure

```
bed-time/
├── src/
│   ├── generate_story.py   # Main script — calls Gemini, saves story
│   ├── scheduler.py        # Alternative: keep-alive Python scheduler
│   └── test_gemini.py      # Connection test — lists available models
├── config/
│   ├── config.yaml         # Age range, themes, sight words, model, schedule time
│   └── .env.example        # Template for .env
├── scripts/
│   ├── run_story.bat       # Entry point used by Windows Task Scheduler
│   └── setup_task.ps1      # Registers the scheduled task (run once, as Admin)
├── stories/                # Generated stories (YYYY-MM-DD.md) — gitignored
├── logs/                   # Task Scheduler output log — gitignored
├── .env                    # Your Gemini API key (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Story Format

Each story is saved as `stories/YYYY-MM-DD.md`:

```markdown
# The Piggy Bank Adventure

**Date:** April 26, 2026
**Theme:** saving money and piggy banks
**Ages:** 6-7

---

Once upon a time, in a cozy little house on Maple Street...
```

---

## Configuration (`config/config.yaml`)

| Key | Description |
|-----|-------------|
| `story.age_range` | Target age group (default: `"6-7"`) |
| `story.max_words` | Target story length in words (default: `350`) |
| `themes` | List of themes — one is picked randomly each day |
| `sight_words` | Grade 1 & 2 Dolch words woven into every story |
| `model.id` | Gemini model ID (use `models/` prefix, e.g. `gemini-flash-latest`) |
| `scheduler.time` | Time for `scheduler.py` alternative (24-hour, e.g. `"20:00"`) |

To see which models are available to your API key:

```
python src\test_gemini.py
```

---

## Manual Commands

| Command | What it does |
|---------|-------------|
| `python src\generate_story.py` | Generate today's story — **skips if already exists**, Gemini API not called |
| `python src\generate_story.py --force` | **Overwrites** today's story even if it exists — calls Gemini API every time |
| `python src\scheduler.py` | Alternative: run a keep-alive Python scheduler |
| `python src\scheduler.py --now` | Same, but also generate a story immediately |
| `python src\test_gemini.py` | List all models available to your API key |

> **Note:** The Windows Task Scheduler always runs without `--force`, so it generates exactly one story per day and never overwrites.
> Use `--force` only when you want to manually regenerate a story — each call hits the Gemini API and overwrites the existing file.

---

## GitHub PR Automation (Optional)

After each story is generated, the script can automatically create a GitHub Pull Request with the new story file.

### Setup

**1. Create a GitHub Personal Access Token**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens) → **Generate new token (classic)**
2. Give it a name (e.g. `bedtime-story-bot`)
3. Check the **`repo`** scope
4. Click **Generate token** and copy it

**2. Add the token to your `.env`**
```
GITHUB_TOKEN=ghp_your_token_here
```

**3. Install the new dependency**
```
pip install -r requirements.txt
```

### What happens automatically

Every time a story is generated:
1. A new branch `story/YYYY-MM-DD` is created
2. The story file is committed to that branch
3. The branch is pushed to GitHub
4. A PR is opened with the story title and theme as the description

### PR output example

```
[PR] Created: https://github.com/dymanojbabu/bed-time/pull/1
```

If `GITHUB_TOKEN` is not set, PR creation is skipped silently — story generation still works normally.

---

## Troubleshooting

**`GEMINI_API_KEY not set`** — Make sure `.env` exists at `C:\Code\bed-time\.env` with your key.

**`429 RESOURCE_EXHAUSTED, limit: 0`** — Your Google account's free tier is blocked. Create a new API key at [aistudio.google.com](https://aistudio.google.com/app/apikey) using a personal Gmail and choose "Create API key in new project".

**`404 NOT_FOUND` for model** — The model name in `config/config.yaml` is wrong. Run `python src\test_gemini.py` to see valid model names. Use the full name including `models/` prefix.

**Task doesn't run** — Open Task Scheduler, find "BedtimeStoryGenerator", right-click → Run to test. Check `logs\story_log.txt` for errors.

**Story already exists** — Run `python src\generate_story.py --force` to overwrite.

**Packages not found** — Run `pip install -r requirements.txt` again with the venv activated: `.venv\Scripts\activate`.
