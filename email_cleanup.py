import imaplib
import email
from getpass import getpass
import datetime

print("🚀 Starting Gmail Cleanup Script")

# ------------------------------
# 1️⃣ LOGIN WITH USER INPUT
# ------------------------------
user_email = input("Enter your Gmail address: ")
app_password = getpass("Enter your Gmail App Password: ")

try:
    print("🔗 Connecting to Gmail IMAP server...")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    print("✅ Connected to IMAP server.")
    
    print(f"🔑 Logging in as {user_email} ...")
    imap.login(user_email, app_password)
    print("✅ Login successful!")
except Exception as e:
    print("❌ ERROR: Login failed.")
    print("Details:", e)
    exit()

# ------------------------------
# 2️⃣ SELECT INBOX
# ------------------------------
try:
    print("📂 Selecting inbox...")
    status, data = imap.select("inbox")
    print(f"✅ Inbox selected. Status={status}, Total Emails={data[0].decode()}")
except Exception as e:
    print("❌ ERROR: Cannot select inbox.")
    print("Details:", e)
    imap.logout()
    exit()

# ------------------------------
# 3️⃣ FETCH EMAIL IDS
# ------------------------------
try:
    print("🔍 Searching for all emails...")
    status, messages = imap.search(None, "ALL")
    if status != "OK":
        print("❌ ERROR: Failed to search emails.")
        imap.logout()
        exit()

    email_ids = messages[0].split()
    print(f"📩 Found {len(email_ids)} emails in inbox.")
except Exception as e:
    print("❌ ERROR: Failed to fetch emails.")
    print("Details:", e)
    imap.logout()
    exit()

# ------------------------------
# 4️⃣ PARSE LAST 10 EMAILS
# ------------------------------
latest_ids = email_ids[-10:]
print(f"📥 Fetching last {len(latest_ids)} emails for processing...")

emails = []
for eid in latest_ids:
    try:
        res, msg_data = imap.fetch(eid, "(RFC822)")
        if res == "OK":
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject = msg.get("subject", "(no subject)")
            sender = msg.get("from", "(no sender)")
            date = msg.get("date", "(no date)")
            emails.append({"id": eid, "subject": subject, "sender": sender, "date": date})
    except Exception as e:
        print(f"⚠️ ERROR fetching email {eid}: {e}")

print(f"✅ Successfully parsed {len(emails)} emails.")

# ------------------------------
# 5️⃣ CLEANUP RULES
# ------------------------------
def is_spam(email_obj):
    spam_keywords = ["prize", "won", "claim", "reward"]
    return any(word in (email_obj["subject"] or "").lower() for word in spam_keywords)

def is_promotion(email_obj):
    promo_keywords = ["sale", "offer", "discount", "deal"]
    return any(word in (email_obj["subject"] or "").lower() for word in promo_keywords)

def is_old(email_obj, days=7):
    try:
        parsed_date = email.utils.parsedate_to_datetime(email_obj["date"])
        return (datetime.datetime.now(datetime.timezone.utc) - parsed_date).days > days
    except Exception:
        return False

keep, delete = [], []

for e in emails:
    if is_spam(e):
        delete.append({**e, "reason": "Spam"})
    elif is_promotion(e) and is_old(e, days=5):
        delete.append({**e, "reason": "Old Promotion"})
    else:
        keep.append(e)

# ------------------------------
# 6️⃣ SHOW RESULTS
# ------------------------------
print("\n📬 Emails to Keep:")
if not keep:
    print("  (No emails kept)")
else:
    for e in keep:
        print(f"  - {e['subject']} ({e['sender']})")

print("\n🗑️ Emails to Delete:")
if not delete:
    print("  (No emails to delete)")
else:
    for e in delete:
        print(f"  - {e['subject']} ({e['sender']}) → {e['reason']}")

choice = input("\n⚠️ Proceed with deletion? (y/N): ").strip().lower()
if choice == "y" and delete:
    for e in delete:
        imap.store(e["id"], "+FLAGS", "\\Deleted")
    imap.expunge()
    print("🗑️ Selected emails deleted (moved to Trash).")
else:
    print("❌ No emails deleted (dry-run mode).")

imap.logout()
print("\n✅ Cleanup Finished.")
