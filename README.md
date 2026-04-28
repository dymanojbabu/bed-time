# Bedtime Story Generator

A free, automated daily bedtime story generator for children aged 6–7.
Every evening at 8 PM, it uses Google Gemini to write a calming one-page
story that weaves in sight words and teaches a gentle life lesson.
Each story is saved as a Markdown file and optionally submitted as a GitHub Pull Request automatically.

---

## Features

- **Free** — Google Gemini free tier via `google-genai` SDK
- **Daily automation** — Windows Task Scheduler fires at 8 PM, no process to babysit
- **Sight word practice** — Grade 1 & 2 Dolch sight words woven naturally into every story
- **20 rotating themes** — saving money, honesty, sharing, helping at home, and more
- **Skip-if-exists** — safe to re-run; won't overwrite today's story unless you pass `--force`
- **GitHub PR automation** — automatically opens a PR with the new story after each generation

---

## Quick-Start (5 steps)

### 1. Get a free Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) signed in with a **personal Gmail** (`@gmail.com`)
2. Click **Create API key → Create API key in new project**
3. Copy the key

> **Important:** Use a personal Gmail (`@gmail.com`), not a work or school account. Work/school Google accounts have the Gemini free tier blocked and will return a `limit: 0` quota error.

### 2. Add your API key

Copy the template to create your `.env` file:

```
cd C:\Code\bed-time
copy config\.env.example .env
```

Open `.env` and fill in your keys:

```
GEMINI_API_KEY=AIza...your_gemini_key...
GITHUB_TOKEN=ghp_...your_github_token...
```

**Important `.env` notes:**
- `.env` must be at the **project root** (`C:\Code\bed-time\.env`), not inside `config/`
- `.env` is listed in `.gitignore` — it will **never be committed to GitHub**, keeping your keys safe
- `config/.env.example` is the safe committed template — it has no real keys
- Never paste real keys into `config/.env.example` or `README.md`

### 3. Install Python dependencies

```
.venv\Scripts\activate
pip install -r requirements.txt
```

> Always activate the virtual environment first. You should see `(.venv)` at the start of your terminal prompt. Without it, packages installed here won't be found when running the scripts.

### 4. Test it manually

```
python src\generate_story.py
```

A story for today is saved in `stories/YYYY-MM-DD.md` and a GitHub PR is opened automatically.

Run with `--force` to regenerate even if today's story already exists:

```
python src\generate_story.py --force
```

### 5. Schedule it (runs every day at 8 PM automatically)

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
C:\Code\bed-time\scripts\setup_task.ps1
```

That's it. The story generates automatically every evening — no terminal needed.

> Your laptop must be **on and not sleeping** at 8 PM. If it's asleep, the task runs the next time it wakes up (the script uses `-StartWhenAvailable`).

---

## File Structure

```
bed-time/
├── src/
│   ├── generate_story.py   # Main script — calls Gemini, saves story, triggers PR
│   ├── github_pr.py        # GitHub PR creation — branches, commits, pushes, opens PR
│   ├── scheduler.py        # Alternative: keep-alive Python scheduler
│   └── test_gemini.py      # Diagnostic — lists available Gemini models
├── config/
│   ├── config.yaml         # Age range, themes, sight words, model, GitHub repo
│   └── .env.example        # Template for .env (safe to commit — no real keys)
├── scripts/
│   ├── run_story.bat       # Entry point used by Windows Task Scheduler
│   └── setup_task.ps1      # Registers the scheduled task (run once, as Admin)
├── stories/                # Generated stories (YYYY-MM-DD.md)
├── logs/                   # Task Scheduler output log
├── .env                    # Your API keys — never commit this
├── .gitignore              # Excludes .env, logs/, .venv/
├── requirements.txt        # Python dependencies
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
| `themes` | List of themes — one picked randomly each day |
| `sight_words` | Grade 1 & 2 Dolch words woven into every story |
| `model.id` | Gemini model ID (e.g. `gemini-flash-latest`) |
| `scheduler.time` | Time for `scheduler.py` alternative (24-hour, e.g. `"20:00"`) |
| `github.repo` | Your GitHub repo in `owner/repo` format (e.g. `dymanojbabu/bed-time`) |

To see which Gemini models are available to your API key:

```
python src\test_gemini.py
```

---

## Manual Commands

| Command | What it does |
|---------|-------------|
| `python src\generate_story.py` | Generate today's story — **skips if already exists**, Gemini API not called |
| `python src\generate_story.py --force` | **Overwrites** today's story even if it exists — calls Gemini and creates a new PR |
| `python src\scheduler.py` | Alternative: keep-alive Python scheduler (runs all day, fires at scheduled time) |
| `python src\scheduler.py --now` | Same, but also generates a story immediately on startup |
| `python src\test_gemini.py` | List all Gemini models available to your API key |
| `python src\github_pr.py` | Create a PR for today's story without regenerating it |

> **`--force` warning:** Each call hits the Gemini API and overwrites the existing story file. The Windows Task Scheduler always runs without `--force`, so it safely generates exactly one story per day.

### When to use `github_pr.py` directly

If the story was already generated today but the PR was skipped (e.g. token wasn't set, network error), you can create the PR without touching Gemini:

```
python src\github_pr.py
```

It reads today's `stories/YYYY-MM-DD.md`, parses the title and theme, and opens the PR. If no story exists for today it will tell you to generate one first.

---

## GitHub PR Automation

After each story is generated, `src/github_pr.py` automatically:

1. Creates a new git branch: `story/YYYY-MM-DD`
2. Commits the story file to that branch
3. Pushes the branch to GitHub
4. Opens a Pull Request with the story title and theme

### PR description example

```
Theme: saving money and piggy banks
File: `2026-04-26.md`

New bedtime story generated automatically.
```

### Setup

**1. Create a GitHub Personal Access Token**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Name: `bedtime-story-bot`
4. Scope: check **`repo`** (full repo access)
5. Click **Generate token** — copy it immediately (shown only once)

**2. Add the token to `.env`**
```
GITHUB_TOKEN=ghp_your_token_here
```

**3. Push your repo to GitHub first**

PRs can only be created if the repo exists on GitHub with a `main` branch:
```
git remote add origin https://github.com/dymanojbabu/bed-time.git
git push -u origin main
```

**4. Test**
```
python src\generate_story.py --force
```

Expected output:
```
Generating today's bedtime story…
Saved  : C:\Code\bed-time\stories\2026-04-26.md
Title  : Leo's Piggy Bank
Theme  : saving money and piggy banks
[PR] Created: https://github.com/dymanojbabu/bed-time/pull/1
```

If `GITHUB_TOKEN` is missing or empty, PR creation is skipped silently — story generation still works normally.

---

## Troubleshooting

**`GEMINI_API_KEY not set`**
Make sure `.env` exists at `C:\Code\bed-time\.env` (not inside `config/`) and contains your key.

**`429 RESOURCE_EXHAUSTED, limit: 0`**
Your Google account's free tier is blocked (usually a work/school account). Create a new key at [aistudio.google.com](https://aistudio.google.com/app/apikey) using a personal Gmail and choose **"Create API key in new project"**.

**`404 NOT_FOUND` for model**
The model name in `config/config.yaml` is not valid. Run `python src\test_gemini.py` to see valid names for your key.

**`ImportError: cannot import name 'genai'`**
The venv Python isn't being used. Activate it first:
```
.venv\Scripts\activate
```
Then run `pip install -r requirements.txt` again.

**`[PR] Git error`**
Make sure you've pushed the repo to GitHub (`git push -u origin main`) and that `github.repo` in `config/config.yaml` matches your actual GitHub repo name.

**Task doesn't run at 8 PM**
Open Task Scheduler → find `BedtimeStoryGenerator` → right-click → **Run** to test manually. Check `logs\story_log.txt` for errors.

**Story already exists**
Run `python src\generate_story.py --force` to overwrite today's story.
