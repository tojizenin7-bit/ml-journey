# =============================================================
# dashboard.py — Local web dashboard using Flask
# -------------------------------------------------------------
# Flask is a micro web framework — it lets Python serve web pages.
# When you run this, your terminal becomes a local web server.
# Open http://localhost:5000 in your browser to see the dashboard.
#
# You'll learn: Flask routing, Jinja2 templates, serving JSON,
# and how front-end (Chart.js) talks to back-end (Python).
# =============================================================

# Flask gives us: Flask (the app), render_template (to serve HTML),
# jsonify (to send JSON), redirect/url_for (for page redirects).
from flask import Flask, render_template, jsonify, redirect, url_for
import storage
import analyzer

# Flask(__name__) creates the app.
# __name__ is a special Python variable — in the main file it's "__main__",
# otherwise it's the module's file name. Flask uses it to find templates/static files.
app = Flask(__name__)


# ---- ROUTES ----
# A 'route' maps a URL path to a Python function.
# @app.route("/") is a DECORATOR — it wraps the function below it
# so Flask knows to call that function when someone visits that URL.

@app.route("/")
def index():
    """
    The homepage — redirects to /dashboard.
    redirect() sends the browser to a different URL.
    url_for("dashboard") generates the URL for the 'dashboard' function.
    This is better than hardcoding "/dashboard" — more maintainable.
    """
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """
    Renders the main dashboard HTML page.

    render_template() looks in the 'templates/' folder for the file,
    fills in any variables you pass, and returns the complete HTML.
    This uses Jinja2 templating — Flask's built-in template engine.
    """
    entries = storage.fetch_all_entries()
    mood    = analyzer.get_mood_trend(entries)
    habits  = analyzer.get_habit_stats(entries)

    # We pass Python variables into the template.
    # In the HTML, {{ mood }} will be replaced with its value.
    return render_template(
        "dashboard.html",
        total_entries = mood.get("total_entries", 0),
        avg_mood      = mood.get("avg", "N/A"),
        trend         = mood.get("trend_direction", "N/A"),
        habit_stats   = habits,
    )


@app.route("/api/mood-chart")
def mood_chart_data():
    """
    Returns mood + energy data as JSON for Chart.js to draw.

    This is an API endpoint — it doesn't return HTML, it returns
    structured data (JSON). The front-end JavaScript fetches this
    and passes it to Chart.js to render charts dynamically.

    JSON (JavaScript Object Notation) is the universal data exchange format
    between front-end and back-end — it looks just like Python dicts/lists.
    """
    entries = storage.fetch_recent_entries(30)   # Last 30 days

    # Build two parallel lists — one for dates (x-axis), one for values (y-axis).
    dates   = [e["date"]   for e in entries]
    moods   = [e["mood"]   for e in entries]
    energys = [e["energy"] for e in entries]

    # jsonify() converts a Python dict to a proper JSON HTTP response.
    return jsonify({
        "labels": dates,
        "mood":   moods,
        "energy": energys,
    })


@app.route("/api/habit-chart")
def habit_chart_data():
    """
    Returns habit completion rates as JSON for a bar chart.
    """
    entries     = storage.fetch_all_entries()
    habit_stats = analyzer.get_habit_stats(entries)

    labels = list(habit_stats.keys())
    # dict.keys() → returns all keys (habit names) as a view object
    # list() converts it to a plain list

    rates  = [habit_stats[h]["rate"] for h in labels]

    return jsonify({"labels": labels, "rates": rates})


@app.route("/api/word-cloud")
def word_cloud_data():
    """
    Returns top words as JSON for the dashboard word display.
    """
    entries = storage.fetch_all_entries()
    words   = analyzer.get_word_frequency(entries, top_n=20)

    # List of dicts — each dict has 'word' and 'count' keys.
    return jsonify([{"word": w, "count": c} for w, c in words])


def run_dashboard():
    """
    Starts the Flask development server.
    Called from cli.py when the user runs: python cli.py serve
    """
    print("\n🌐  Starting LifeLog dashboard...")
    print("   Open your browser at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server.\n")

    # debug=True → auto-reloads when you save changes to the code.
    # NEVER use debug=True in production (public servers) — only for local dev.
    # use_reloader=False avoids a Flask quirk where it starts twice in some envs.
    app.run(debug=True, use_reloader=False, port=5000)