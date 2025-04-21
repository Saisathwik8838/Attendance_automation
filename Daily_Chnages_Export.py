import csv
import os
import datetime
import pandas as pd
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# File Paths
SAVE_DIR = os.path.expanduser(r"C:\Users\saisa\OneDrive\Desktop\google_photos_project")
ALBUMS_CSV = os.path.join(SAVE_DIR, "albums_data.csv")
DAILY_CHANGES_CSV = os.path.join(SAVE_DIR, "daily_changes.csv")
ATTENDANCE_CSV = os.path.join(SAVE_DIR, "attendance.csv")

# Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "cseaattendance@gmail.com"
SENDER_PASSWORD = "jtjd qyni axyq jcan"
DOMAIN = "@iiitdwd.ac.in"

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_album_data(filename):
    if not os.path.exists(filename):
        return {}, "No Data"

    with open(filename, mode="r", newline="") as file:
        reader = csv.reader(file)
        data = list(reader)

    if len(data) < 2:
        return {}, "Not Enough Data"

    headers = data[0]
    if len(headers) < 3:
        return {}, "Not Enough Columns"

    latest_col, prev_col = headers[-1], headers[-2]
    album_changes = {}

    for row in data[1:]:
        album = row[0]
        try:
            latest_count = int(row[-1]) if row[-1].isdigit() else 0
            prev_count = int(row[-2]) if row[-2].isdigit() else 0
        except ValueError:
            latest_count, prev_count = 0, 0

        album_changes[album] = max(0, latest_count - prev_count)

    return album_changes, latest_col

def export_daily_changes(album_changes, date_label, filename=DAILY_CHANGES_CSV):
    ensure_directory_exists(SAVE_DIR)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    file_exists = os.path.exists(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Albums", "New Photos Added", "Timestamp", "Date Label"])

        for album, new_photos in album_changes.items():
            writer.writerow([album, new_photos, timestamp, timestamp])

    print(f"✅ Daily changes saved to {filename} at {timestamp}")

def update_attendance_csv(daily_changes_file=DAILY_CHANGES_CSV, attendance_file=ATTENDANCE_CSV):
    if not os.path.exists(daily_changes_file):
        print("⚠️ No daily_changes.csv found, skipping attendance update.")
        return

    daily_df = pd.read_csv(daily_changes_file)

    if daily_df.empty or "Date Label" not in daily_df.columns:
        print("⚠️ daily_changes.csv is empty or missing expected columns.")
        return

    daily_df["Albums"] = daily_df["Albums"].astype(str).str.strip()
    daily_df["Date Label"] = pd.to_datetime(daily_df["Date Label"].astype(str).str.strip(), errors="coerce")
    daily_df["New Photos Added"] = pd.to_numeric(daily_df["New Photos Added"], errors="coerce").fillna(0).astype(int)

    daily_df = daily_df.dropna(subset=["Date Label"])
    if daily_df.empty:
        print("⚠️ No valid rows with date info in daily_changes.csv.")
        return

    latest_timestamp = daily_df["Date Label"].max()
    column_label = latest_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    today_df = daily_df[daily_df["Date Label"] == latest_timestamp]

    if today_df.empty:
        print(f"⚠️ No matching entries for {latest_timestamp}.")
        return

    today_df["present"] = today_df["New Photos Added"].apply(lambda x: 1 if x > 0 else 0)
    today_attendance = dict(zip(today_df["Albums"], today_df["present"]))

    if os.path.exists(attendance_file):
        attendance_df = pd.read_csv(attendance_file)
    else:
        attendance_df = pd.DataFrame(columns=["albums"])

    attendance_df["albums"] = attendance_df["albums"].astype(str).str.strip()

    all_albums = set(attendance_df["albums"]).union(today_attendance.keys())
    attendance_df = attendance_df.set_index("albums").reindex(all_albums, fill_value=0).reset_index()

    attendance_df[column_label] = attendance_df["albums"].apply(lambda x: today_attendance.get(x, 0))

    attendance_df.to_csv(attendance_file, index=False)
    print(f"✅ Attendance updated for {column_label} in {attendance_file}")

def get_absent_students():
    if not os.path.exists(DAILY_CHANGES_CSV):
        print("❌ CSV file not found!")
        return []

    df = pd.read_csv(DAILY_CHANGES_CSV, dtype=str)

    if "Albums" not in df.columns or "New Photos Added" not in df.columns:
        print("❌ Required columns not found in CSV!")
        return []

    latest_timestamp = df["Date Label"].max()
    df_latest = df[df["Date Label"] == latest_timestamp]

    absent_students = []
    for _, row in df_latest.iterrows():
        roll_number = str(row["Albums"]).strip()
        email = f"{roll_number}{DOMAIN}"

        try:
            photo_change = int(row["New Photos Added"]) if row["New Photos Added"].isdigit() else 0
        except ValueError:
            print(f"⚠️ Invalid data for {roll_number}. Skipping.")
            continue

        if photo_change == 0:
            absent_students.append(email)

    return absent_students

def send_absent_email(email):
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

    time.sleep(1)

def check_and_notify_absent_students():
    absent_students = get_absent_students()

    if not absent_students:
        print("✅ No absent students today. No emails sent.")
        return

    print(f"📩 Sending emails to {len(absent_students)} absent students...")

    for email in absent_students:
        send_absent_email(email)

if __name__ == "__main__":
    album_changes, latest_col = load_album_data(ALBUMS_CSV)
    if album_changes:
        export_daily_changes(album_changes, latest_col)
        update_attendance_csv()
        check_and_notify_absent_students()
    else:
        print("❌ Not enough data in albums.csv to compute changes.")
