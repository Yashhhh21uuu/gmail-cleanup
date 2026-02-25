# cleanup/routes.py
from flask import Blueprint, request, jsonify
from cleanup.email_handler import smart_cleanup, undo_quarantine
import traceback

cleanup_bp = Blueprint("cleanup", __name__)

@cleanup_bp.route("/cleanup", methods=["POST"])
def cleanup_route():
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "Email & password are required"}), 400

        # ✅ FIXED: pass as positional arguments
        result = smart_cleanup(
            email,
            password,
            [d.strip() for d in data.get("domains", "").split(",") if d.strip()],
            [k.strip() for k in data.get("keywords", "").split(",") if k.strip()],
            int(data.get("older_than_days", data.get("days", 30))),
            data.get("action", "quarantine"),
            bool(data.get("dry_run", True)),
        )

        print(f"[SMART CLEANUP] {result.get('count', 0)} emails matched for {email}")
        return jsonify(result)

    except Exception as e:
        print("[ERROR in cleanup_route]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@cleanup_bp.route("/undo", methods=["POST"])
def undo_route():
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "Email & password are required"}), 400

        result = undo_quarantine(email, password)
        print(f"[UNDO] Restored {result.get('count', 0)} emails for {email}")
        return jsonify(result)

    except Exception as e:
        print("[ERROR in undo_route]", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
