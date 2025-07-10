import os
import requests
import pandas as pd
import win32com.client as win32
from datetime import datetime

# Configuration
CSV_URL = "https://ticketformv1.onrender.com/download"
LOCAL_CSV_PATH = "C:\\Users\\ppombrio\\Documents\\tickets.csv"  # Adjust this if needed

# Step 1: Download latest CSV
try:
    response = requests.get(CSV_URL)
    response.raise_for_status()
    with open(LOCAL_CSV_PATH, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("✅ CSV downloaded successfully.")
except Exception as e:
    print(f"❌ Failed to download CSV: {e}")
    exit()

# Step 2: Load CSV
try:
    df = pd.read_csv(LOCAL_CSV_PATH)
    df = df.dropna(subset=['due_date'])  # Filter out blank due dates
except Exception as e:
    print(f"❌ Failed to read CSV: {e}")
    exit()

# Step 3: Initialize Outlook
outlook = win32.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
calendar = namespace.GetDefaultFolder(9).Items  # 9 = olFolderCalendar
calendar.IncludeRecurrences = True
calendar.Sort("[Start]")

# Get existing subjects to avoid duplicates
existing_subjects = {item.Subject.lower() for item in calendar}

# Step 4: Create calendar events
for _, row in df.iterrows():
    name = row.get("name", "")
    title = row.get("title", "")
    category = row.get("category", "General")
    due_date_str = row.get("due_date", "")
    created_date_str = row.get("created_date", "")
    
    # Format dates
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        continue  # Skip invalid date

    try:
        start_date = datetime.strptime(created_date_str, "%Y-%m-%d")
    except ValueError:
        start_date = due_date

    subject = f"TICKET: {title.strip()}"
    if subject.lower() in existing_subjects:
        continue  # Skip if already added

    # Create new calendar event
    appointment = outlook.CreateItem(1)  # 1 = olAppointmentItem
    appointment.Subject = subject
    appointment.Start = start_date
    appointment.End = due_date
    appointment.Body = f"{title}\nSubmitted by: {name}\nCategory: {category}"
    appointment.Categories = category
    appointment.ReminderSet = True
    appointment.ReminderMinutesBeforeStart = 60
    appointment.Save()
    print(f"✅ Event created: {subject}")
