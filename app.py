import bcrypt
import json
import os
import threading
from datetime import datetime
from functools import wraps

from flask import Flask, request, redirect, render_template, make_response, send_file
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")
CURRENT_FILE = os.path.join(os.path.dirname(__file__), "current.txt")
os.makedirs(HISTORY_DIR, exist_ok=True)

busy = False


def check_auth():
    return request.cookies.get(config.COOKIE_NAME) == "authenticated"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


def set_current(ts):
    with open(CURRENT_FILE, "w") as f:
        f.write(ts)


def get_current_entry():
    if not os.path.exists(CURRENT_FILE):
        return None, None
    with open(CURRENT_FILE) as f:
        ts = f.read().strip()
    frame = os.path.join(HISTORY_DIR, ts, "frame.png")
    if not os.path.exists(frame):
        return None, None
    return ts, frame


def get_all_entries():
    entries = sorted(os.listdir(HISTORY_DIR), reverse=True)
    return [e for e in entries if os.path.exists(os.path.join(HISTORY_DIR, e, "frame.png"))]


def push_in_background(frame_path):
    global busy
    busy = True
    def push():
        global busy
        try:
            import display
            display.push_to_display(frame_path)
        finally:
            busy = False
    threading.Thread(target=push, daemon=True).start()


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "").encode()
        if bcrypt.checkpw(password, config.PASSWORD_HASH.encode()):
            response = make_response(redirect("/"))
            response.set_cookie(
                config.COOKIE_NAME,
                "authenticated",
                max_age=config.COOKIE_MAX_AGE,
                httponly=True,
                samesite="Strict",
            )
            return response
        error = "Incorrect password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    response = make_response(redirect("/login"))
    response.delete_cookie(config.COOKIE_NAME)
    return response


@app.route("/")
@login_required
def index():
    timestamp, _ = get_current_entry()
    return render_template("index.html", timestamp=timestamp, history=get_all_entries())


@app.route("/current")
@login_required
def current():
    _, frame = get_current_entry()
    if frame is None:
        return "", 404
    return send_file(frame, mimetype="image/png")


@app.route("/history/<ts>/image")
@login_required
def history_image(ts):
    frame = os.path.join(HISTORY_DIR, ts, "frame.png")
    if not os.path.exists(frame):
        return "", 404
    return send_file(frame, mimetype="image/png")


@app.route("/history/<ts>/resend", methods=["POST"])
@login_required
def history_resend(ts):
    frame = os.path.join(HISTORY_DIR, ts, "frame.png")
    if not os.path.exists(frame):
        return redirect("/")
    set_current(ts)
    push_in_background(frame)
    return redirect("/")


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("image")
    text = request.form.get("text", "").strip()

    has_image = file and file.filename != ""
    if has_image:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            has_image = False

    if not has_image and not text:
        return redirect("/")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    entry_dir = os.path.join(HISTORY_DIR, timestamp)
    os.makedirs(entry_dir, exist_ok=True)

    raw_path = None
    if has_image:
        raw_path = os.path.join(entry_dir, "original.png")
        file.save(raw_path)

    from compose import compose
    composed = compose(image_path=raw_path, text=text)

    frame_path = os.path.join(entry_dir, "frame.png")
    composed.save(frame_path)

    with open(os.path.join(entry_dir, "meta.json"), "w") as f:
        json.dump({"timestamp": timestamp, "text": text}, f)

    set_current(timestamp)
    push_in_background(frame_path)
    return redirect("/")


@app.route("/api/status")
@login_required
def api_status():
    return {"busy": busy}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
