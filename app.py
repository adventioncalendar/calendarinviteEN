from flask import Flask, Response
from datetime import datetime, timedelta, date
import uuid

app = Flask(__name__)

def ics_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )

def dtstamp_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

def yyyymmdd(d: date):
    return d.strftime("%Y%m%d")

def add_months(d: date, months: int) -> date:
    """Add months to a date without external libs."""
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    # clamp day to last day of target month
    # (handles e.g., Jan 31 + 1 month -> Feb 28/29)
    import calendar
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()
    start0 = now.date()  # dynamic "download date" (UTC)

    # Three events spaced 1 month apart
    starts = [start0, add_months(start0, 1), add_months(start0, 2)]

    title = "Pick up your HIVST"
    descriptions = [
        "Please go to your local medical centre (Reminder 1)",
        "Please go to your local medical centre (Reminder 2)",
        "Please go to your local medical centre (Reminder 3)",
    ]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, start_date in enumerate(starts):
        uid = f"{uuid.uuid4()}@ics-generator"
        dtstart = yyyymmdd(start_date)
        dtend = yyyymmdd(start_date + timedelta(days=1))

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp_utc(now)}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            # Repeat every 3 months forever (so 3 events interleave to monthly forever)
            "RRULE:FREQ=MONTHLY;INTERVAL=3",
            f"SUMMARY:{ics_escape(title)}",
            f"DESCRIPTION:{ics_escape(descriptions[i])}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ics = "\r\n".join(lines) + "\r\n"

    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=invite.ics"},
    )

@app.route("/")
def health():
    return "OK. Try /invite.ics"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)







