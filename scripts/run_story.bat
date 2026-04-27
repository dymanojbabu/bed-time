@echo off
cd /d "C:\Code\bed-time"
if not exist logs mkdir logs
python src\generate_story.py >> logs\story_log.txt 2>&1
