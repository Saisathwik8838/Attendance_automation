# 📸 Google Photos Attendance System

This project automates attendance using Google Photos albums. It checks whether students' photos are present in an album on a given day and sends absent notifications via email.

---

## 🚀 Features

- 🔐 OAuth2 authentication with Google Photos API
- 📊 Tracks photo count changes in `albums_data.csv`
- 📆 Computes daily photo additions and stores in `daily_changes.csv`
- 📧 Sends automatic email alerts to absent students

---

## 🛠 Folder Structure

google_photos_project/ │ ├── authenticate.py # Handles Google API OAuth authentication├── fetch_albums.py # Fetches albums from Google Photos
├── export_to_csv.py # Exports album photo counts to CSV
├── Daily_chnages.py # Compares current and previous counts
├── check_and_notify.py # Sends email to students with no photo change
├── albums_data.csv # Tracks photo count over time
├── daily_changes.csv # Daily photo differences 
├── client_secret.json # OAuth client credentials 
├── token.json # Stores access + refresh tokens 
└── README.md # Project documentation (this file)

To make this project work you first need to have the gmail id and the password with which I created the Auoth authentication and project in google cloud console etc.
