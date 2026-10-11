"""Email sender. Uses Gmail SMTP app-password from env. Dry-run prints."""
import os
import smtplib
from email.mime.text import MIMEText

def send(results, to_addr=None):
    to_addr = to_addr or os.getenv("ALERT_EMAIL_TO")
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    lines = []
    for r in results:
        if r.get("signal"):
            lines.append(f"SIGNAL {r['pair']} {r['direction']} entry={r['entry']:.2f} "
                         f"SL={r['sl']:.2f} TP={r['tp']:.2f} RR={r['rr']:.2f} grade={r['grade']}")
        else:
            lines.append(f"NO TRADE {r['pair']}: {r.get('reason')}")
    body = "\n".join(lines)
    if not (to_addr and user and pwd):
        print("--- EMAIL DRY-RUN ---")
        print(body)
        return False
    msg = MIMEText(body)
    msg["Subject"] = "[SMC-AGENT] Daily scan"
    msg["From"] = user
    msg["To"] = to_addr
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)
    print("email sent")
    return True
