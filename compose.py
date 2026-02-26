from PIL import Image, ImageDraw, ImageFont, ImageOps

FRAME_W = 800
FRAME_H = 480
PADDING = 16
FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_SIZE = 30
TEXT_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)


def _load_font():
    try:
        return ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        return ImageFont.load_default()


def _fit(img, w, h):
    """Resize img to fit within (w, h), letterboxing with black."""
    img = img.convert("RGB")
    img.thumbnail((w, h), Image.LANCZOS)
    frame = Image.new("RGB", (w, h), BG_COLOR)
    frame.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return frame


def _wrap_text(text, font, max_width):
    """Wrap text so each line fits within max_width pixels."""
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if dummy.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _open(image_path):
    """Open image, apply EXIF rotation, and rotate portrait images to landscape."""
    img = ImageOps.exif_transpose(Image.open(image_path).convert("RGB"))
    if img.height > img.width:
        img = img.rotate(-90, expand=True)
    return img


def compose(image_path=None, text=None):
    font = _load_font()
    text = text.strip() if text else ""

    if not text:
        return _fit(_open(image_path), FRAME_W, FRAME_H)

    img = _open(image_path) if image_path else None

    # For portrait images, wrap text to the portrait image's width so it
    # sits neatly under the image rather than spanning the full frame width.
    if img and img.height > img.width:
        text_w = int(FRAME_H * img.width / img.height)  # estimated portrait width
    else:
        text_w = FRAME_W
    text_x = (FRAME_W - text_w) // 2  # horizontal offset to center the text block

    lines = _wrap_text(text, font, text_w - 2 * PADDING)
    line_h = FONT_SIZE + 8
    band_h = len(lines) * line_h + PADDING * 2

    frame = Image.new("RGB", (FRAME_W, FRAME_H), BG_COLOR)

    if img:
        frame.paste(_fit(img, FRAME_W, FRAME_H - band_h), (0, 0))
        band_y = FRAME_H - band_h
    else:
        band_y = (FRAME_H - band_h) // 2

    draw = ImageDraw.Draw(frame)
    y = band_y + PADDING
    for line in lines:
        x = text_x + (text_w - int(draw.textlength(line, font=font))) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += line_h

    return frame
