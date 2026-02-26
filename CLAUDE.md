# E-Ink Display — Claude Context

## Raspberry Pi Access

- **SSH:** `ssh oliverkuehle@inky`
- **Password:** stored in `config.py` (not committed)
- **Python virtualenv:** `source ~/.virtualenvs/pimoroni/bin/activate` — always use this
- **App location:** `/home/oliverkuehle/inky-hagen/`
- **System service:** `myapp` — starts the webapp on boot
  - After code changes: `sudo systemctl restart myapp`
  - Run manually: `source ~/.virtualenvs/pimoroni/bin/activate && python app.py`

## Display Hardware

- **Model:** Inky Impression 7.3" (Spectra 6 panel)
- **Resolution:** 800 × 480 px
- **Color palette:** 7 colors — Black, White, Red, Green, Blue, Yellow, Orange
- **Library:** Pimoroni `inky` (installed in pimoroni virtualenv)

## Tech Stack

| Component        | Choice                              |
|------------------|-------------------------------------|
| Web framework    | Flask                               |
| Image processing | Pillow (PIL)                        |
| Display library  | `inky` (Pimoroni)                   |
| Password hashing | `bcrypt`                            |
| Frontend         | Vanilla HTML/CSS/JS (no build step) |
| Storage          | Local filesystem (no database)      |

## File Structure

```
inky-hagen/
├── app.py              # Flask app — all routes
├── compose.py          # Image composition (Pillow)
├── display.py          # Inky display logic
├── config.py           # Password hash + secret key (gitignored)
├── current.txt         # Pointer to currently displayed history entry (gitignored)
├── .gitignore
├── history/            # All past frames (gitignored)
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── frame.png       # Final composed image (800×480)
│       ├── original.png    # Raw upload
│       └── meta.json       # {timestamp, text}
└── templates/
    ├── login.html
    └── index.html
```

## config.py (not committed — create manually on the Pi)

```python
PASSWORD_HASH = "$2b$12$..."   # bcrypt hash — generate with:
                                # python3 -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"
SECRET_KEY = "..."             # random string — generate with:
                                # python3 -c "import secrets; print(secrets.token_hex(32))"
COOKIE_NAME = "auth"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year
```

## Key Decisions

- Images are always auto-rotated to landscape (portrait images rotated 90°) to fill the 800×480 frame
- Text is always: black, white background, size S (30px), bottom of frame, centered
- Image upload only — no direct camera capture
- No upload size limit
- History stored indefinitely, not deletable from UI
- Password changeable via `config.py` only
