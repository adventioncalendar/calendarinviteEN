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
    events_data =  [
    ("Protektahan ang iyong sarili at ang iyong kapareha sa pamamagitan ng HIV self-testing","May bago ka bang partner o hindi sigurado sa HIV status ng iyong kapareha? Ang self-test ay makatutulong upang manatili kang kampante at maprotektahan ang mahalaga sa iyo. Ang regular na pagpapasuri ay nagbibigay sa iyo ng kontrol sa iyong kalusugan at sumusuporta sa pag-iwas sa HIV."),
    ("Kumpirmahin ang iyong HIV status matapos ang posibleng exposure: Gumamit ng HIV self-test ngayon","Nagkaroon ba ng hindi protektadong pakikipagtalik o napunit ang condom? Gumamit ng HIV self-test sa lalong madaling panahon. Kung ang exposure ay nangyari sa loob ng nakaraang 72 oras, magpatingin agad para sa PEP. Ang maagap na pagkilos ay makatutulong upang manatili kang protektado at may tamang kaalaman."),
    ("Maghanda para sa iyong quarterly PrEP refill sa pamamagitan ng HIV self-test ngayon","Ikaw ba ay gumagamit ng PrEP o nagpapatuloy sa HIV prevention? Kung umiinom ka ng araw-araw na oral PrEP, mag-HIV self-test nang hindi bababa sa bawat 3 buwan. Ang regular na pagsusuri ay tumutulong upang manatiling ligtas, epektibo, at tuloy-tuloy ang iyong PrEP routine."),
    ("Maging kumpiyansa habang gumagamit o muling nagsisimula ng PrEP sa pamamagitan ng HIV self-test ngayon","Huminto ka ba o nagbabalak muling magsimula ng PrEP? Bago ka magsimula muli, kumpirmahin muna ang iyong HIV-negative status gamit ang self-test. Ang regular na pagsusuri ay tumutulong na maprotektahan ka at mapanatiling epektibo ang iyong prevention plan."),
    ("Kontrolin ang iyong kalusugan sa pamamagitan ng HIV self-test ngayon","Ang pakiramdam na malusog ay hindi palaging nangangahulugang wala kang HIV. Maraming tao ang walang nararanasang sintomas sa mga unang yugto. Ang self-test ay nagbibigay sa iyo ng malinaw na kasagutan, kumpiyansa, at kontrol sa iyong HIV status."),
    ("Gawing bahagi ng iyong personalized na pangangalaga ang HIV self-testing matapos ang pahinga sa PrEP","Hindi mo ba matandaan kung kailan ka huling nagpa-test? Ngayon ay magandang panahon upang mag-HIV self-test. Ang regular na pagsusuri ay tumutulong sa maagang pagtuklas at nagbibigay ng kumpiyansa sa iyong HIV prevention journey."),
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





