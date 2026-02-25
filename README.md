# gmail-cleanup
# 📬 MailTrim – Gmail Cleanup & Smart Inbox Manager

MailTrim is a Python-based Gmail cleanup system that connects via IMAP, analyzes inbox emails, and safely removes unwanted messages using a structured dry-run workflow.

It is designed to automate inbox hygiene while ensuring user control and safety.

---

## 🚀 Key Features

### 🔐 Secure Gmail IMAP Integration
- Connects using Gmail App Password
- Authenticates via IMAP over SSL
- Fetches latest N emails from inbox

---

### 📥 Email Parsing Engine
- Extracts:
  - Sender
  - Subject
  - Body preview
- Detects system emails
- Handles newsletter and notification emails

---

### 🧠 Smart Cleanup Logic
- Separates emails into:
  - 📬 Emails to Keep
  - 🗑 Emails to Delete
- Conservative filtering approach (safe-first design)
- Designed to prevent accidental deletion

---

### 🛑 Dry-Run Safety Mode
Before deleting anything, the system:

1. Displays emails marked for deletion  
2. Asks for user confirmation  
3. Proceeds only if user approves  

This ensures zero accidental data loss.

---

## 🏗 Architecture Overview
#run-python email_cleanup.py
#output
📂 Selecting inbox...
📩 Found 17 emails in inbox.

📬 Emails to Keep:
 - Security alert
 - Meeting reminder

🗑 Emails to Delete:
 (No emails to delete)

⚠ Proceed with deletion? (y/N):
