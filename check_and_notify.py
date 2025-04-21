import smtplib
import time
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "cseaattendance@gmail.com"  # Change this
SENDER_PASSWORD = "jtjd qyni axyq jcan"  # Use an App Password
CSV_FILE = r"C:\Users\saisa\OneDrive\Desktop\google_photos_project\daily_changes.csv"  # Updated CSV file location
DOMAIN = "@iiitdwd.ac.in"  # Email domain

def get_absent_students():
    """Reads the 'daily_changes.csv' and returns emails of absent students."""
    if not os.path.exists(CSV_FILE):
        print("❌ CSV file not found!")
        return []

    df = pd.read_csv(CSV_FILE, dtype=str)  # Read CSV as strings

    if "Albums" not in df.columns or "New Photos Added" not in df.columns:
        print("❌ Required columns not found in CSV!")
        return []

    absent_students = []
    for _, row in df.iterrows():
        roll_number = str(row["Albums"]).strip()
        email = f"{roll_number}{DOMAIN}"

        try:
            photo_change = int(row["New Photos Added"]) if row["New Photos Added"].isdigit() else 0
        except ValueError:
            print(f"⚠️ Invalid data for {roll_number}. Skipping.")
            continue

        if photo_change == 0:  # Only add students marked as Absent
            absent_students.append(email)

    return absent_students

def send_absent_email(email):
    """Sends an email notification if the student is absent."""
    subject = "🚨 Attendance Alert - You Are Marked Absent"

    body = """
    <h2>Attendance Notification</h2>
    <p><b>Your photo was not detected in the album, and you are marked as <span style='color:red;'>Absent</span>.</b></p>
    <p>Please ensure your images are added correctly before the next attendance check.</p>
    """

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {email} (Absent)")

    except Exception as e:
        print(f"❌ Email to {email} failed: {e}")

    time.sleep(1)  # Small delay to prevent rate limits

def check_and_notify_absent_students():
    """Finds absent students and sends them email notifications."""
    absent_students = get_absent_students()

    if not absent_students:
        print("✅ No absent students today. No emails sent.")
        return

    print(f"📩 Sending emails to {len(absent_students)} absent students...")

    for email in absent_students:
        send_absent_email(email)

if __name__ == "__main__":
    check_and_notify_absent_students()
