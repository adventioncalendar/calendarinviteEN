from flask import Flask, Response
from datetime import datetime, timedelta, date
import uuid
import calendar

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
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()
    base_date = now.date()  # dynamic start = download date (UTC)

    # 6 different events (each repeats every 6 months; together = monthly forever)
    events_data = [
        ("Protect yourself and your partner with HIV self-testing","Seeing someone new or unsure of a partner’s HIV status? A self-test helps you stay confident and protect what matters. Testing regularly keeps you in control of your health and supports prevention."),
        ("Confirm your HIV status after a possible exposure: Use an HIV self-test now","Had unprotected sex or a condom break? Take an HIV self-test as soon as possible. If exposure was within the last 72 hours, seek PEP immediately. Acting early helps you stay protected and informed."),
        ("Prepare for your quarterly PrEP refill by taking an HIV self-test now","On PrEP or continuing prevention? If you’re taking daily oral PrEP, self-test for HIV at least every 3 months. Regular testing keeps your PrEP routine safe, effective, and on track."),
        ("Be confident while on, or when looking to restart, PrEP by taking an HIV self-test now","Paused or thinking of restarting? Before you begin again, confirm your HIV-negative status with a self-test. Regular testing protects you and keeps your prevention plan working."),
        ("Take control of your health by taking an HIV self-test now","Feeling healthy doesn’t always mean HIV-free. Many people have no early symptoms. A self-test gives you clarity, confidence, and control over your status."),
        ("Make HIV self-testing part of your personalized care after a break from PrEP","Not sure when you last tested? Now is a great time to self-test. Regular testing helps you detect early and stay confident in your prevention journey."), 
    ]

    # Alerts:
    # - Day before: midnight the day before (relative to all-day start at 00:00)
    alarm_day_before = "TRIGGER;RELATED=START:-P1D"
    # - Day of: 9am local time on the day (00:00 + 9 hours)
    alarm_day_of = "TRIGGER;RELATED=START:PT9H"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, (title, description) in enumerate(events_data):
        start_date = add_months(base_date, i)
        end_date = start_date + timedelta(days=1)

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@ics-generator",
            f"DTSTAMP:{dtstamp_utc(now)}",
            f"DTSTART;VALUE=DATE:{yyyymmdd(start_date)}",
            f"DTEND;VALUE=DATE:{yyyymmdd(end_date)}",
            "RRULE:FREQ=MONTHLY;INTERVAL=6",
            f"SUMMARY:{ics_escape(title)}",
            f"DESCRIPTION:{ics_escape(description)}",

            # Alert 1: day before
            "BEGIN:VALARM",
            alarm_day_before,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            # Alert 2: day of (9am)
            "BEGIN:VALARM",
            alarm_day_of,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

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





