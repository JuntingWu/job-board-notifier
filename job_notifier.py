from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import json
import time
import smtplib
from email.mime.text import MIMEText


URL = "https://ecc-uoft-coop-csm.symplicity.com/students/app/jobs/search?perPage=20&page=1&sort=!postdate"
CHECK_INTERVAL = 1800  # seconds (30 min)
SESSION_FILE = "auth.json"

load_dotenv()
SENDER = os.getenv("EMAIL_SENDER")
RECEIVER = os.getenv("EMAIL_RECEIVER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, PASSWORD)
        server.send_message(msg)


def fetch_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto(URL)
        page.wait_for_selector("a.job-title", timeout=15000)

        jobs = []
        for job in page.query_selector_all("a.job-title"):
            title = job.inner_text().strip()
            link = job.get_attribute("href")
            jobs.append({"title": title, "link": link})
        browser.close()
        return jobs


def main():
    try:
        with open("seen_jobs.json") as f:
            seen = json.load(f)
    except FileNotFoundError:
        seen = []

    while True:
        print("Checking for new jobs...")
        try:
            jobs = fetch_jobs()
        except Exception as e:
            print("Fetch failed:", e)
            time.sleep(CHECK_INTERVAL)
            continue

        new_jobs = [j for j in jobs if j["title"] not in [s["title"] for s in seen]]

        if new_jobs:
            body = "\n\n".join([f"{j['title']}\n{j['link']}" for j in new_jobs])
            send_email("New Co-op Job(s) Posted!", body)
            print("Sent notification for:", [j["title"] for j in new_jobs])
            seen.extend(new_jobs)
            with open("seen_jobs.json", "w") as f:
                json.dump(seen, f, indent=2)
        else:
            print("No new jobs found.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
