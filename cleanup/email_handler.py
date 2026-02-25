# cleanup/email_handler.py
import imaplib, email, json
from email.utils import parsedate_to_datetime, parseaddr
from datetime import datetime, timedelta, timezone

def connect_imap(user, password, server="imap.gmail.com", port=993):
    imap = imaplib.IMAP4_SSL(server, port)
    imap.login(user, password)
    return imap

def list_uids(imap, folder="INBOX"):
    imap.select(folder)
    typ, data = imap.uid("search", None, "ALL")
    return [uid.decode() for uid in data[0].split()] if data and data[0] else []

def fetch_headers(imap, uid):
    typ, data = imap.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
    if typ != "OK" or not data or data[0] is None:
        return None
    return email.message_from_bytes(data[0][1])



def filter_emails(imap, uids, domains, keywords, older_than_days):
    matched = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

    for uid in uids:
        status, data = imap.fetch(uid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(data[0][1])
        from_addr = msg.get("From", "").lower()
        subject = msg.get("Subject", "").lower()
        date_str = msg.get("Date")

        msg_date = None
        if date_str:
            try:
                msg_date = email.utils.parsedate_to_datetime(date_str)
                if msg_date.tzinfo is None:
            # If it's naive, make it UTC-aware
                    msg_date = msg_date.replace(tzinfo=timezone.utc)
                else:
            # Convert to UTC to match cutoff
                    msg_date = msg_date.astimezone(timezone.utc)
            except Exception:
                pass  #

        if any(d in from_addr for d in domains) or \
           any(k in subject for k in keywords) or \
           (msg_date and msg_date < cutoff):
            matched.append({"uid": uid, "from": from_addr, "subject": subject, "date": str(msg_date)})

    return matched


def ensure_folder(imap, name):
    try:
        imap.create(name)
    except:
        pass

def move_to_folder(imap, matches, target="MailTrim-Quarantine", expunge=False):
    ensure_folder(imap, target)
    moved = []
    for m in matches:
        uid = m["uid"]
        res, _ = imap.uid("COPY", uid, target)
        if res == "OK":
            imap.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
            moved.append(m)
    if expunge:
        imap.expunge()
    return moved

def smart_cleanup(user, password, domains=None, keywords=None, older_than_days=30, action="quarantine", dry_run=True):
    try:
        imap = connect_imap(user, password)
    except Exception as e:
        return {"status": "error", "message": f"IMAP login failed: {str(e)}"}

    try:
        uids = list_uids(imap)
        if not uids:
            return {"status": "no_emails", "message": "No emails found in inbox."}

        matched = filter_emails(imap, uids, domains or [], keywords or [], older_than_days)
        if not matched:
            return {"status": "no_emails", "message": "No emails matched your filters."}

        if dry_run:
            return {"status": "success", "count": len(matched), "samples": matched[:20]}

        target = "MailTrim-Quarantine" if action == "quarantine" else action
        moved = move_to_folder(imap, matched, target, expunge=(action == "trash"))

        return {"status": "success", "count": len(moved), "moved": moved}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        try:
            imap.logout()
        except:
            pass


def undo_quarantine(user, password):
    imap = connect_imap(user, password)
    try:
        imap.select("MailTrim-Quarantine")
        typ, data = imap.uid("search", None, "ALL")
        if typ != "OK" or not data or not data[0]:
            return {"restored": 0}
        uids = [uid.decode() for uid in data[0].split()]
        restored = []
        for uid in uids:
            res, _ = imap.uid("COPY", uid, "INBOX")
            if res == "OK":
                imap.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
                restored.append(uid)
        imap.expunge()
        return {"restored": len(restored)}
    finally:
        imap.logout()
