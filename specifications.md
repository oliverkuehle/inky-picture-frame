# E-Ink Display Web Server — Specifications

## Overview

A Flask web server running on a Raspberry Pi connected to an **Inky Impression 7.3"** e-ink display (800 × 480 px). The server exposes a web UI accessible to family members for composing and pushing images (with optional text) to the display.

---

## Authentication

- Single shared family password stored as a **bcrypt hash** in `config.py`
- Unauthenticated users are redirected to `/login`
- On successful login, a **secure HTTP-only, SameSite=Strict cookie** is set (1 year lifetime)
- All routes and API endpoints require authentication

---

## Main Page

### 1. Current Display Panel

- Shows the image currently on the e-ink display as a preview
- Shows the timestamp of when it was last pushed
- Reflects whichever frame was most recently sent — whether a new upload or a history re-send

### 2. New Frame Panel

- **Image upload** — JPEG or PNG, optional
- **Text** — optional free text
- Either image, text, or both must be provided
- Pressing **Send to Display** composes and pushes the frame, then redirects (Post/Redirect/Get)
- While the display is updating, a full-page loading overlay is shown to all users

### 3. History Timeline

- Horizontally scrollable list of all past frames (thumbnail + timestamp)
- Clicking any entry re-sends that exact frame to the display
- Stored indefinitely, never deleted via UI

---

## Image Processing Pipeline

When a new frame is submitted:

1. Save the raw upload as `original.png`
2. Apply EXIF rotation correction
3. If the image is portrait (height > width), rotate 90° to landscape
4. Fit the image into the frame (letterboxed with white), respecting any text band space
5. If text is provided, render a white band with black text along the bottom edge
6. Save the composed 800×480 result as `frame.png`
7. Push to the display via the `inky` library (in a background thread)
8. Save `meta.json` with timestamp and text
9. Update `current.txt` to point to this entry

### Text Rendering

- Font: LiberationSans Bold, size 30px
- Color: black on white background
- Position: bottom of frame
- Text wraps automatically; band height expands to fit
- Text is centered horizontally

### Text-Only Frames

If no image is provided, the text is centered vertically on a white 800×480 canvas.

---

## Loading State

- Server maintains an in-memory `busy` flag set while the display is refreshing
- Browser polls `GET /api/status` every 1.5 seconds
- While busy: full-page overlay with spinner and "Updating display…"
- When done: page reloads automatically to show the updated current image

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page (requires auth) |
| GET/POST | `/login` | Login form |
| GET | `/logout` | Clears cookie, redirects to login |
| POST | `/upload` | Submit new frame |
| GET | `/current` | Serves the current frame.png |
| GET | `/history/<ts>/image` | Serves a history frame by timestamp |
| POST | `/history/<ts>/resend` | Re-sends a history frame to the display |
| GET | `/api/status` | Returns `{"busy": true/false}` |

---

## Storage

```
history/
└── YYYY-MM-DD_HH-MM-SS/
    ├── frame.png       # Final 800×480 composed image
    ├── original.png    # Raw upload
    └── meta.json       # {"timestamp": "...", "text": "..."}

current.txt             # Contains the timestamp of the currently displayed entry
```

---

## Security

- bcrypt password hashing (timing-safe)
- HTTP-only, SameSite=Strict cookie
- File type validation (JPEG/PNG only)
- No upload size limit
- No shell commands constructed from user input
- `config.py` is gitignored (contains password hash and secret key)
