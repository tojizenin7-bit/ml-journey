
# exporter.py — export your data to CSV or Markdown

# Real-world apps always need export functionality.
# You'll learn: writing files, the csv module, f-strings for
# text formatting, and the os module for path handling.


import csv        # Built-in module for reading/writing CSV files
import os         # For creating directories and building file paths
from datetime import date

import storage
import analyzer


# Exports folder — all exported files go here.
EXPORT_DIR = "exports"


def _ensure_export_dir():
        """
    Creates the exports/ directory if it doesn't already exist.
    The leading underscore marks this as a private helper.
    """
    # os.makedirs creates the directory (and any parent dirs) if missing.
    # exist_ok=True means: don't raise an error if it already exists.
        os.makedirs(EXPORT_DIR, exist_ok=True)


def export_csv():
    """
    Writes all entry data to a CSV file.

    CSV (Comma Separated Values) is universally readable —
    Excel, Google Sheets, pandas, R — everything opens it.
    """
    _ensure_export_dir()

    entries = storage.fetch_all_entries()
    if not entries:
        print("📭  No data to export yet.")
        return

    # Build the file path using os.path.join — works on all operating systems.
  
    # On Mac/Linux: exports/lifelog_export.csv
    filename = os.path.join(EXPORT_DIR, "lifelog_export.csv")

    #    with open(filename, "w") as f' opens a file for writing.
    # w mode → write (creates or overwrites the file)
    # a mode → append (adds to existing file)
    #  newline="" is required for csv.writer to avoid blank lines on Windows.
    with open(filename, "w", newline="", encoding="utf-8") as f:

            # csv.writer handles commas, quotes, and newlines automatically.
        writer = csv.writer(f)

        # Write the header row first.
        writer.writerow(["date", "mood", "energy", "note"] + [h for h in _get_all_habit_names(entries)])
        # List concatenation: [a, b] + [c, d] → [a, b, c, d]

        for entry in entries:
            habits = storage.fetch_habits_for_entry(entry["id"])
            habit_done = {h["name"]: h["done"] for h in habits}
            # Dict comprehension: {key: value for item in iterable}
            # Builds a dict like {"exercise": 1, "water": 0, ...}

            row = [
                entry["date"],
                entry["mood"],
                entry["energy"],
                entry["note"] or "",
            ]
            # Add habit done/not-done values in consistent order
            for h_name in _get_all_habit_names(entries):
                row.append(habit_done.get(h_name, 0))
                # .get(key, default) → returns 0 if habit_name not found

            writer.writerow(row)

    print(f"✅  CSV exported to: {filename}")


def export_markdown_report():
    """
    Generates a human-readable Markdown report file.

    Markdown (.md) files are great for GitHub — they render beautifully.
    This is what a professional "Weekly Review" document looks like.
    """
    _ensure_export_dir()

    entries  = storage.fetch_all_entries()
    if not entries:
        print("📭  No data to export yet.")
        return

    today    = date.today().isoformat()
    filename = os.path.join(EXPORT_DIR, f"report_{today}.md")

    mood         = analyzer.get_mood_trend(entries)
    habit_stats  = analyzer.get_habit_stats(entries)
    correlations = analyzer.get_mood_vs_habits_correlation(entries)
    top_words    = analyzer.get_word_frequency(entries, top_n=10)

    # ---- Build the Markdown content ----
    # We use a list of lines and join them at the end — this is more efficient
    # than string concatenation (each '+' creates a new string object in memory).
    lines = []

    # Markdown syntax:
    #   # Heading 1     ## Heading 2     **bold**     `code`
    #   | col | col |   --- (table divider)

    lines.append(f"# 📊 LifeLog Report — {today}\n")
    lines.append(f"_Generated automatically by LifeLog_\n")

    lines.append(f"## 😊 Mood Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total entries | {mood.get('total_entries', 0)} |")
    lines.append(f"| Average mood  | {mood.get('avg', 'N/A')}/10 |")
    lines.append(f"| Highest mood  | {mood.get('high', 'N/A')}/10 |")
    lines.append(f"| Lowest mood   | {mood.get('low', 'N/A')}/10 |")
    lines.append(f"| Trend         | {mood.get('trend_direction', 'N/A')} |")
    lines.append("")

    lines.append(f"## ✅ Habit Completion\n")
    lines.append(f"| Habit | Completion Rate | Current Streak |")
    lines.append(f"|-------|----------------|---------------|")
    for habit, s in habit_stats.items():
        lines.append(f"| {habit} | {s['rate']}% | 🔥 {s['streak']} days |")
    lines.append("")

    if correlations:
        lines.append(f"## 🔗 Habits That Boost Your Mood\n")
        lines.append(f"| Habit | Mood with | Mood without | Impact |")
        lines.append(f"|-------|-----------|--------------|--------|")
        for c in correlations:
            sign = "+" if c["mood_impact"] > 0 else ""
            lines.append(f"| {c['habit']} | {c['avg_with']} | {c['avg_without']} | {sign}{c['mood_impact']} |")
        lines.append("")

    if top_words:
        lines.append(f"## 📝 Most Common Words in Notes\n")
        word_str = ", ".join(f"**{w}** ({c})" for w, c in top_words)
        lines.append(word_str)
        lines.append("")

    lines.append(f"---")
    lines.append(f"_LifeLog — your personal data, your insights._")

    # Join all lines with newlines and write to file.
    content = "\n".join(lines)

    with open(filename, "w", encoding="utf-8") as f:
        # encoding="utf-8" ensures emoji and special characters save correctly
        f.write(content)

    print(f"✅  Markdown report saved to: {filename}")


def _get_all_habit_names(entries: list) -> list:
    """
    Helper: returns a sorted list of unique habit names across all entries.
    Used to build consistent CSV column headers.
    """
    names = set()   # A set automatically removes duplicates
    for entry in entries:
        habits = storage.fetch_habits_for_entry(entry["id"])
        for h in habits:
            names.add(h["name"])   # .add() inserts into the set
    return sorted(names)           # sorted() returns a sorted list from any iterable